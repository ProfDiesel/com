from com.ledger import kvdataclass
from typing import List, Tuple, Final
import asyncio
import nats

SessionId = str
UnderlyingName = str

@kvdataclass
class PricingState:
    subscriptions: List[Tuple[SessionId, UnderlyingName]]


async def main():
    nc = await nats.connect('nats://a:a@localhost:4222')
    js = nc.jetstream()
    kv = await js.key_value(bucket='JL-pricing_state')

    state: Final[PricingState] = await PricingState.load(kv)

    s = await state.subscriptions.reduce(lambda x: x + ['', ''])
    print(s)

asyncio.run(main())
