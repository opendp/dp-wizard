"""
TITLE
"""

# Install the following dependencies, if you haven't already:
# pip install DEPENDENCIES

from argparse import ArgumentParser

IMPORTS_BLOCK

UTILS_BLOCK

COLUMNS_BLOCK


def get_context_contributions(csv_path):
    CONTEXT_BLOCK
    return context, contributions


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Creates a differentially private release from a csv"
    )
    parser.add_argument(
        "--csv", required=True, help="Path to csv containing private data"
    )
    args = parser.parse_args()
    context, contributions = get_context_contributions(csv_path=args.csv)

    QUERIES_BLOCK
