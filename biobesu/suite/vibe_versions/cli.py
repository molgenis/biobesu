#!/user/bin/env python3

from biobesu.helper.generic import retrieve_entry_point
from biobesu.helper.argument_parser import BiobesuParser


def main(parser):
    # Load available runners.
    runners = retrieve_entry_point('biobesu_vibe_versions')

    # Adds suite-specific command line.
    parser.add_argument('runner', help='a runner from this suite:\n' +
                                       '\n'.join(runners))

    # Processes command line.
    args, unknown_args = parser.parse_known_args()

    # Run selected runner.
    runners[args.runner](parser)


if __name__ == '__main__':
    main(BiobesuParser())
