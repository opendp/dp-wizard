from argparse import ArgumentParser

import polars as pl
import opendp.prelude as dp

dp.enable_features("contrib")


def get_context(csv_path):
    privacy_unit = dp.unit_of(contributions=1)

    context = dp.Context.compositor(
        data=pl.scan_csv(csv_path, encoding="utf8-lossy"),
        privacy_unit=privacy_unit,
        privacy_loss=dp.loss_of(epsilon=1),
        split_by_weights=[1],
    )

    return context


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Creates a differentially private release from a csv"
    )
    parser.add_argument("--csv", help="Path to csv containing private data")
    args = parser.parse_args()
    context = get_context(csv_path=args.csv)
    print(context)
