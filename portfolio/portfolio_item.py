"a single item in the user's portfolio of stocks"

class PortfolioItem(object):
    def __init__(self, symbol=None, num_shares=0, purchase_price=0.0):
        self.symbol=symbol
        self.num_shares=num_shares
        self.purchase_price=purchase_price

    def __eq__(self, b):
        return self.__dict__ == b.__dict__

    def __repr__(self):
        return "PortfolioItem(symbol={symbol}, num_shares={num_shares}, pprice={purchase_price})".format(**self.__dict__)

        
