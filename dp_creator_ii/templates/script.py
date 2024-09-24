from argparse import ArgumentParser
IMPORTS_CODE


def get_context(csv_path):
    CONTEXT_CODE
    return context


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Creates a DP release from a given CSV.')
    parser.add_argument(
        '--csv',
        help='Path to CSV containing private data')
    args = parser.parse_args()
    context = get_context(csv_path=args.csv)
    print(context)
