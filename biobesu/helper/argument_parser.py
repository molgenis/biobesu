#!/user/bin/env python3

from argparse import ArgumentParser
import sys as sys


class BiobesuParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n\n" % message)
        self.print_help()
        print()
        sys.exit(2)