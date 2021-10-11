#!/user/bin/env python3

from biobesu.suite.vibe_versions.runner.vibe_5_0 import VibeRunner5_0
from biobesu.helper.argument_parser import BiobesuParser


class VibeRunner5_1(VibeRunner5_0):
    JAR_FILENAME = 'vibe-with-dependencies-5.1.5.jar'
    HDT_FILENAME = 'vibe-5.1.0.hdt'
    OUTPUT_SUBDIR = '5.1/'
    FINAL_OUTPUT_FILE = 'vibe_5.1.0.tsv'


def main(parser):
    VibeRunner5_1(parser).run()


if __name__ == '__main__':
    main(BiobesuParser())
