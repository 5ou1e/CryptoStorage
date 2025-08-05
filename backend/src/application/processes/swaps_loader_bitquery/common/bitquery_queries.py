import datetime

from src.domain.constants import SOL_ADDRESS


def get_dex_trades(
    start_time: datetime,
    end_time: datetime,
    offset: int = 0,
    limit: int | None = None,
):
    if limit is None:
        limit = 100000

    query = """
{
  Solana {
    DEXTrades(
      limit: {count: %d, offset: %d}
      orderBy: {ascending: Transaction_Signature}
      where: {
        Block: {
          Time: {
            after: "%s"
            before: "%s"
          }
        }
      }
    ) {
      Trade {
        Buy {
          Amount
          Currency {
            Symbol
            MintAddress
          }
          Price
        }
        Sell {
          Amount
          Currency {
            Symbol
            MintAddress
          }
        }
      }
      Block {
        Time
        Slot
      }
      Transaction {
        Signature
        Signer
      }
    }
  }
}
    """ % (
        limit,
        offset,
        start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    )

    return query
