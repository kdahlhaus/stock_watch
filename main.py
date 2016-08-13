import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty

from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window

from Datagrid import DataGrid
from price_input import PriceInput
from integer_input import IntegerInput

import csv


class StockEntry(object):
    def __init__(self, symbol=None, num_shares=0, purchase_price=0.0):
        self.symbol=symbol
        self.num_shares=num_shares
        self.purchase_price=purchase_price

    def __repr__(self):
        return "StockEntry(symbol={symbol}, num_shares={num_shares}, pprice={purchase_price})".format(**self.__dict__)

        


class YahooStockPrices():

    def __init__(self, on_results=None, on_error=None):
        self.symbols = []
        self.on_results=on_results
        self.on_error=on_error
        self.prices = {}

    def add_symbol(self, symbol):
        self.symbols.append(symbol)

    def get_prices(self):
        if len(self.symbols)>0:
            symbol_param=""
            for symbol in self.symbols:
                symbol_param += "+" + symbol
            symbol_param = symbol_param[1:]
            self.req = UrlRequest("http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sbagh"%symbol_param, 
                              on_success=self.got_yahoo_prices, 
                              on_failure=self.got_yahoo_error, 
                              on_error=self.got_yahoo_error,
                              on_redirect=self.on_redirect,
                              )

    def got_yahoo_prices(self, request, results):
        #print results, len(results), type(results)
        quote_reader = csv.reader(results.splitlines())
        for row in quote_reader:
            self.prices[row[0]]=row
        if self.on_results:
            self.on_results(self.prices)



    def got_yahoo_error(self, request, results=None):
        print "error: %s %s"%(request, results)
        if self.on_error:
            self.on_error("error " + str(request)+" "+str(results))


    def on_redirect(self, *args):
        print "on_redirect:"+str(args)
        if self.on_error:
            self.on_error("redirect " + str(args))


 

class MainWindow(TabbedPanel):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.stock_grid = self.ids.stock_grid
        self.existing_stock_setup_grid = self.ids.existing_stock_setup_grid
        cw = Window.width / 5
        self.stock_grid.setupGrid( [{'text':"Stock", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Price", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Day Low", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Day High", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Total Gain(Loss)", 'type':'BorderLabel', 'width':cw}],  Window.width, 46)

        cw = Window.width / 4
        self.existing_stock_setup_grid.setupGrid([{'text':"Stock", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Num Shares", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Purchase Price", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Remove", 'type':'BorderLabel', 'width':cw} ], Window.width, 46)




class StockWatch(App):

    refresh_button = ObjectProperty()
    rendered_stock_data = StringProperty("")

    stock_entries = []

    #                symbol  #     purchase price
    stocks = { "KEY":(2500, 11.47), "GM":(3300, 30.367), "CMI":(0,1), "NFLX":(0,1)   }


    def on_error(self, *args):
        print "on_error: " + str(args)


    def render_setup_screen_stocks(self):
        self.main_window.ids.existing_stock_setup_grid.removeAllContent()
        for e in self.stock_entries:
            temp_data = [ {"text":e.symbol, "type":"Label"},
                         {'text':str(e.num_shares), 'type':'Label'},
                         {'text':"${:.2f}".format(e.purchase_price), 'type':'Label'},
                     {'text':"x", 'type':'Button'} ]
            self.main_window.ids.existing_stock_setup_grid.addRow(temp_data)
 

    def on_add_new_stock(self, *args):
        symbol = self.main_window.ids.stock_input.text
        #TODO: validate symbol
        num_shares = int(self.main_window.ids.num_shares_input.text)
        price = float(self.main_window.ids.price_input.text)
        new_entry = StockEntry( symbol, num_shares, price)
        print "new entry: {}".format(new_entry)
        self.stock_entries.append(new_entry)
        self.render_setup_screen_stocks()






    def refresh_prices(self):
        self.pricer = YahooStockPrices(self.on_new_prices, self.on_error)
        symbols = set()
        for stock_entry in self.stock_entries:
            symbols.add(stock_entry.symbol)
        for symbol in symbols:
            self.pricer.add_symbol(symbol)
        self.pricer.get_prices()



    def on_new_prices(self, prices):
        stock_data =[]
        for entry in self.stock_entries:
            price_data = prices[entry.symbol]
            price = float(price_data[1])
            day_low=float(price_data[3])
            day_high=float(price_data[2])

            total_gain_or_loss = entry.num_shares*(price-entry.purchase_price)
            stock_data.append( { "symbol":entry.symbol, "price":price, "total_gain_or_loss":total_gain_or_loss, "day_low":day_low, "day_high":day_high } )


        """
        for symbol in prices.keys():
            print symbol, prices[symbol]
            price = float(prices[symbol][1])
            num_shares=self.stocks[symbol][0]
            orig_price=self.stocks[symbol][1]
            day_low=float(prices[symbol][3])
            day_high=float(prices[symbol][2])
            total_gain_or_loss = num_shares*(price-orig_price)
            stock_data.append( { "symbol":symbol, "price":price, "total_gain_or_loss":total_gain_or_loss, "day_low":day_low, "day_high":day_high } )
            """
        self.render_new_stock_data(stock_data)            



    def render_new_stock_data( self, stock_data ):                              

        # display the given list of stock data
        total = 0.0
        #text = ""
        #text += "{symbol:>8}:   {price:10} {dl:>8} {dh:>8}   {total_gain_or_loss:14}\n".format(symbol="Stock", price="Current Price", total_gain_or_loss="Total Gain", dh="Day High", dl="Day Low")
        self.main_window.stock_grid.removeAllContent()
        for row in stock_data:
            temp_data = [{'text':row['symbol'], 'type':'Label'}, 
                         {'text':"${:.2f}".format(row['price']), 'type':'Label'},
                         {'text':"${:.2f}".format(row['day_low']), 'type':'Label'},
                         {'text':"${:.2f}".format(row['day_high']), 'type':'Label'},
                         {'text':"${:.2f}".format(row['total_gain_or_loss']), 'type':'Label'}]
            total += float(row["total_gain_or_loss"])
            self.main_window.stock_grid.addRow(temp_data)

            #text += "{symbol:>8}:   {price: 8.2f}  {day_low: 8.2f}  {day_high: 8.2f}    {total_gain_or_loss: 12.2f}\n".format(**row)
        temp_data = [{'text':'', 'type':'Label'}, 
                    {'text':"", 'type':'Label'},
                    {'text':"", 'type':'Label'},
                    {'text':"total:", 'type':'Label'},
                    {'text':"${:.2f}".format(total), 'type':'Label'}] 
        self.main_window.stock_grid.addRow(temp_data)
        #self.rendered_stock_data = text        


    def build(self):
        self.main_window = MainWindow()
        return self.main_window


if __name__ == '__main__':
    StockWatch().run()
