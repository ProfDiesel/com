ProductId = str
UnderlyingId = str

@dataclass
class Product:
    id: ProductId
    ric: str
    underlying: UnderlyingId
    maturity: datetime

@expose
def underlyings() -> Collection[UnderlyingId]:
    return Underlyings.select(Underlyings.name).fetch_all()

@expose
def products(underlying: UnderlyingId, maturity: Optional[daetime] = None) -> Collection[Product]:
    req = Products.where(Products.underlying == underlying)
    if maturity is not None:
        req = req.select(Product.maturity == maturity)
    return req.fetch_all()
