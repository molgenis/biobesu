#!/user/bin/env python3

from argparse import RawTextHelpFormatter
from biobesu.helper.generic import retrieve_entry_point
from biobesu.helper.argument_parser import BiobesuParser


def main():
    # Load available suites.
    suites = retrieve_entry_point('biobesu_suites')

    # Defines global command line.
    parser = BiobesuParser(formatter_class=RawTextHelpFormatter, add_help=False)
    parser.add_argument('suite', help='the chosen benchmark suite:\n' + '\n'.join(suites))

    # Processes command line.
    args, unknown_args = parser.parse_known_args()

    # Run selected suite.
    suites[args.suite](parser)


if __name__ == '__main__':
    main()
