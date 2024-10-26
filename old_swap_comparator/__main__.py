import asyncio
import csv
import os
import datetime

from swap_comparator.utils.utils_1inch import run_1inch


def write_on_timestamp(path: str, data: list[dict], timestamp: datetime.datetime):
    file_exists = os.path.isfile(path)

    with open(path, "a") as csvfile:
        # "timestamp",
        # "chain",
        # "token_in",
        # "token_out",
        # "pair_metadata",
        # "platform",
        # "amount_in",
        # "amount_out",
        headers = [
            "timestamp",
            "fromToken",
            "toToken",
            "chainId",
            "gasCostAmount",
            "amountIn",
            "amountOut",
        ]
        writer = csv.DictWriter(csvfile, delimiter=",", lineterminator="\n", fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        for row in data:
            writer.writerow(row)


async def run_each_hour():
    current_datetime = datetime.datetime.now()
    datetime_up_to_hour = current_datetime.replace(minute=0, second=0, microsecond=0)
    data = []

    await asyncio.gather(
        run_1inch(data, datetime_up_to_hour),
    )

    write_on_timestamp(os.path.join("data", "timestamp.csv"), data)


async def main():
    run_each_hour()


if __name__ == "__main__":
    asyncio.run(main())
