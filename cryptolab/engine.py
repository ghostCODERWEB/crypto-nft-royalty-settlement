"""Split sale proceeds among seller, marketplace and royalty recipients with exact integer conservation."""

from .common import (
    number,
    integer,
    identity,
    records,
    chronology,
    allocate,
    result,
    validate_document,
)
from decimal import Decimal


def _analyze(d):
    market_bps = integer(d["market_bps"], maximum=10000)
    royalties = records(d["royalties"], "recipient")
    bps = {r["recipient"]: integer(r["bps"], maximum=10000) for r in royalties}
    total_bps = sum(bps.values()) + market_bps
    if total_bps > 10000:
        raise ValueError("fees exceed gross proceeds")
    rows = []
    totals = {r: 0 for r in bps}
    market = 0
    sellers = {}
    for sale in records(d["sales"], "id"):
        price = integer(sale["price"])
        seller = identity(sale["seller"])
        payments = {r: price * v // 10000 for r, v in bps.items()}
        fee = price * market_bps // 10000
        net = price - fee - sum(payments.values())
        market += fee
        sellers[seller] = sellers.get(seller, 0) + net
        for r, v in payments.items():
            totals[r] += v
        rows.append(
            {
                "id": sale["id"],
                "gross": price,
                "seller_net": net,
                "market_fee": fee,
                "royalties": payments,
            }
        )
    return {
        "sales": rows,
        "royalty_totals": totals,
        "market_total": market,
        "seller_totals": sellers,
        "gross": sum(r["gross"] for r in rows),
    }


def analyze(document):
    validate_document(document)
    try:
        return result(_analyze(document))
    except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
        raise ValueError("invalid domain input: " + str(error)) from error
