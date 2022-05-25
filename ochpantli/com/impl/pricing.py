from datetime import datetime, timedelta
from enum import Enum, auto
from typing import NewType, Optional

from numpy import exp, log, sqrt
from scipy.stats import norm

from ..services.pricing import (Book, Indicator, Product, PricingServer, ProductKind, Spot, Strike)
from ..types import SessionId

UnderlyingName = NewType('UnderlyingName', str)
Spot = NewType('Spot', float)
Strike = NewType('Strike', float)

class Underlying:
    def spot(self) -> Spot:
        pass

    def volatility(self) -> float:
        pass

    def interest_rate(self) -> float:
        pass

    def cont_div(self) -> float:
        pass

class OptionType(Enum):
    CALL = auto()
    PUT = auto()

class Option(Product):
    @property
    def underlying(self) -> UnderlyingName:
        pass

    def strike(self) -> Strike:
        pass

    def maturity(self) -> datetime:
        pass

    def underlying(self) -> Underlying:
        pass

    def type(self) -> OptionType:
        pass


# https://www.nasdaq.com/market-activity/stocks/aapl/historical
def option_premium(s: Spot, k: Strike, m: datetime, r, cont_div, vol, type_, now: datetime):

    #S: spot price
    #K: strike price
    #T: time to maturity
    #r: interest rate
    #cont_div: rate of continuous dividend paying asset
    #vol: volatility of underlying asset

    t: timedelta = m - now

    d1 = (log(s / k) + (r - cont_div + 0.5 * vol ** 2) * t) / (vol * sqrt(t))
    d2 = (log(s / k) + (r - cont_div - 0.5 * vol ** 2) * t) / (vol * sqrt(t))

    if type_ == OptionType.CALL:
        return (s * exp(-cont_div * t) * norm.cdf(d1, 0.0, 1.0) - k * exp(-r * t) * norm.cdf(d2, 0.0, 1.0))
    else:
        return (k * exp(-r * t) * norm.cdf(-d2, 0.0, 1.0) - s * exp(-cont_div * t) * norm.cdf(-d1, 0.0, 1.0))


class PricingServerImpl(PricingServer):
    def price(self, book: Book) -> float:
        pass

    async def continuous_pricing(self, session: SessionId, book: Book):
        self.__ledger.update(f'registrations/{book}', lambda value: value + [book])

    async def price_indicator(self, product: Product, indicator: Indicator):
        if indicator == 'premium':
            return self.product_premium(self, product)
        if indicator == 'delta':
            if product.kind == ProductKind.OPTION:
                spot = product.underlying.spot
                spot_delta = spot * 0.01
                return (self.product_premium(self, product, spot - spot_delta / 2) + self.product_premium(self, product, spot - spot_delta / 2)) / spot_delta

    def product_premium(self, product: Product, spot: Optional[Spot] = None):
        if product.kind == ProductKind.OPTION:
            underlying = product.underlying
            option_premium(spot or underlying.spot, product.strike, product.maturity, underlying.interest_rate, product.cont_div, product.vol, product.type, datetime.now())
