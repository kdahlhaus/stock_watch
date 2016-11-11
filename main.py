import kivy
kivy.require('1.0.6') # replace with your current kivy version !


from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.uix.behaviors.focus import FocusBehavior  #https://kivy.org/docs/api-kivy.uix.behaviors.focus.html
from kivy.utils import platform
from kivy.logger import Logger as logging

# UI imports, some used implicitly by the GUI loader
from data_grid_plugin.Datagrid import DataGrid
from widgets.price_input import PriceInput
from widgets.integer_input import IntegerInput


from portfolio.portfolio_item import PortfolioItem
from stock_price_providers.yahoo_provider import YahooStockPriceProvider

if platform=="android":
    DATA_GRID_ROW_HEIGHT = 80
else:
    DATA_GRID_ROW_HEIGHT=25





class MainWindow(TabbedPanel):

    on_tab_switch = None

    def switch_to(self, header):
        TabbedPanel.switch_to(self, header)
        if self.on_tab_switch:
            self.on_tab_switch(header)

 

    def __init__(self):
        super(MainWindow, self).__init__()
        self.stock_grid = self.ids.stock_grid
        self.existing_stock_setup_grid = self.ids.existing_stock_setup_grid
        cw = Window.width / 5
        self.stock_grid.setupGrid( [{'text':"Stock", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Price", 'type':'BorderLabel', 'width':cw},
                                      {'text':"Day Low", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Day High", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Total", 'type':'BorderLabel', 'width':cw}],  Window.width, DATA_GRID_ROW_HEIGHT)

        cw = Window.width / 4
        self.existing_stock_setup_grid.setupGrid([{'text':"Stock", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Num Shares", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Purchase Price", 'type':'BorderLabel', 'width':cw},
                                    {'text':"Remove", 'type':'BorderLabel', 'width':cw} ], Window.width, DATA_GRID_ROW_HEIGHT)




class StockWatch(App):

    refresh_button = ObjectProperty()
    rendered_stock_data = StringProperty("")

    portfolio = [PortfolioItem("KEY", 2500, 11.47), PortfolioItem("GM", 3300, 30.367),
                     PortfolioItem("CMI", 0, 0), PortfolioItem("NFLX", 0, 0) ]



    #TODO: clean up store - make attribute of app

    def save_portfolio(self):
        store = JsonStore('stockwatch.json')
        json_compatible_data = []
        for entry in self.portfolio:
            json_compatible_data.append(entry.__dict__)
        store['portfolio']= { 'entries':json_compatible_data } 

    def load_portfolio(self):
        self.portfolio=[]
        store = JsonStore('stockwatch.json')
        if 'portfolio' in store:
            dicts = store.get("portfolio")['entries']
            for d in dicts:
                s = PortfolioItem()
                s.__dict__=d
                self.portfolio.append(s)
        if len(self.portfolio)==0:
            self.portfolio.append(PortfolioItem("Key", 2500, 11.34))
            self.portfolio.append(PortfolioItem("GM", 1000, 34.01))
            self.portfolio.append(PortfolioItem("CMI", 300, 30))

    def on_tab_switch(self, tab_header):
        "wired to be called on tab switch"
        if tab_header.text == "Setup":   # TODO: switch to objects to avoid text value coupling
            self.render_setup_screen_stocks()
        elif tab_header.text=="Stock Value":
            self.refresh_prices()

    def on_error(self, *args):
        print "on_error: " + str(args)

    def on_delete_entry(self, *args, **kwargs):
        entry = kwargs['entry']
        self.portfolio.remove(entry)
        self.render_setup_screen_stocks()
        self.save_portfolio()


    def render_setup_screen_stocks(self):
        self.main_window.ids.existing_stock_setup_grid.removeAllContent()
        for i,e in enumerate(self.portfolio):
            temp_data = [ {"text":e.symbol, "type":"Label"},
                         {'text':str(e.num_shares), 'type':'Label'},
                         {'text':"${:.2f}".format(e.purchase_price), 'type':'Label'},
                         {'text':"x", 'type':'Button', 'callback':self.on_delete_entry, 'params':{'entry':e, 'index':i} } ]
            self.main_window.ids.existing_stock_setup_grid.addRow(temp_data)
 

    def on_add_new_stock(self, *args):
        symbol = self.main_window.ids.stock_input.text
        #TODO: validate symbol
        num_shares = int(self.main_window.ids.num_shares_input.text)
        price = float(self.main_window.ids.price_input.text)

        new_entry = PortfolioItem( symbol, num_shares, price)
        self.portfolio.append(new_entry)

        self.save_portfolio()
        self.render_setup_screen_stocks()

        self.main_window.ids.stock_input.text=""
        self.main_window.ids.num_shares_input.text=""
        self.main_window.ids.price_input.text=""






    def refresh_prices(self):
        "kick off async call to get updated stock proces"
        self.pricer = YahooStockPriceProvider(self.on_new_prices, self.on_error)  # TODO provide other stock price providers
        symbols = set()
        for stock in self.portfolio:
            symbols.add(stock.symbol)
        for symbol in symbols:
            self.pricer.add_symbol(symbol)
        self.pricer.get_prices()



    def on_new_prices(self, prices):
        "callback when new price data comes in"
        stock_data =[]
        for entry in self.portfolio:
            price_data = prices[entry.symbol]
            price = float(price_data[1]) if price_data[1] != "N/A" else 0.0
            day_low=float(price_data[3]) if price_data[3] != "N/A" else 0.0
            day_high=float(price_data[2]) if price_data[2] != "N/A" else 0.0

            if price != 0.0:
                total_gain_or_loss = entry.num_shares*(price-entry.purchase_price)
            else:
                total_gain_or_loss = 0.0
            stock_data.append( { "symbol":entry.symbol, "price":price, "total_gain_or_loss":total_gain_or_loss, "day_low":day_low, "day_high":day_high } )

        self.render_new_stock_data(stock_data)            



    def render_new_stock_data( self, stock_data ):                              
        "render a set of stock data on the main screen"

        # display the given list of stock data
        total = 0.0
        self.main_window.stock_grid.removeAllContent()
        for row in stock_data:
            temp_data = [{'text':row['symbol'], 'type':'Label'}, 
                         {'text':"${:.2f}".format(row['price']), 'type':'Label'},
                         {'text':"${:.2f}".format(row['day_low']), 'type':'Label'},
                         {'text':"${:.2f}".format(row['day_high']), 'type':'Label'},
                         {'text':"${:.0f}".format(row['total_gain_or_loss']), 'type':'Label'}]
            total += float(row["total_gain_or_loss"])
            self.main_window.stock_grid.addRow(temp_data)

            #text += "{symbol:>8}:   {price: 8.2f}  {day_low: 8.2f}  {day_high: 8.2f}    {total_gain_or_loss: 12.2f}\n".format(**row)
        temp_data = [{'text':'', 'type':'Label'}, 
                    {'text':"", 'type':'Label'},
                    {'text':"", 'type':'Label'},
                    {'text':"Total:", 'type':'Label'},
                    {'text':"${:.0f}".format(total), 'type':'Label'}] 
        self.main_window.stock_grid.addRow(temp_data)
        #self.rendered_stock_data = text        


    def build(self):
        self.main_window = MainWindow()
        self.main_window.on_tab_switch = self.on_tab_switch
        self.load_portfolio()
        return self.main_window




    def on_pause(self):
        # Here you can save data if needed
        logging.info("pausing")
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        logging.info("resuming")


if __name__ == '__main__':
    logging.info("DATA_GRID_ROW_HEIGHT %d"%DATA_GRID_ROW_HEIGHT)
    logging.debug("DATA_GRID_ROW_HEIGHT %d"%DATA_GRID_ROW_HEIGHT)

    StockWatch().run()
