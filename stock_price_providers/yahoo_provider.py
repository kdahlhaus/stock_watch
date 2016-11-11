from kivy.network.urlrequest import UrlRequest

import csv


class YahooStockPriceProvider(object):

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
