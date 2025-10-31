# TITLE
#
# CUSTOM_NOTE

# Install the following dependencies, if you haven't already:
# WINDOWS_COMMENT_BLOCK
#
# $ pip install DEPENDENCIES

from argparse import ArgumentParser

IMPORTS_BLOCK

DESCRIPTION_COLUMNS_BLOCK


def get_stats_context_contributions(csv_path):
    DESCRIPTION_CONTEXT_BLOCK
    # ENCODING_COMMENT_BLOCK
    return stats_context, contributions


if __name__ == "__main__":
    parser = ArgumentParser(description="Describes the columns of a csv")
    parser.add_argument(
        "--csv", required=True, help="Path to csv containing private data"
    )
    args = parser.parse_args()
    stats_context, contributions = get_stats_context_contributions(csv_path=args.csv)

    DESCRIPTION_QUERIES_BLOCK
