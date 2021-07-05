#!/user/bin/env python3

from subprocess import call
from biobesu.helper import validate
from biobesu.helper.generic import create_dir
from biobesu.helper.readers import SeparatedValuesFileReader
from biobesu.suite.vibe_versions.helper.converters import convert_list_to_arguments_with_same_key
from biobesu.suite.vibe_versions.helper.converters import merge_vibe_simple_output_files
from biobesu.helper.argument_parser import BiobesuParser

# Used only for docstring
from argparse import ArgumentParser


class VibeRunner5_0:
    JAR_FILENAME = 'vibe-with-dependencies-5.0.3.jar'
    HDT_FILENAME = 'vibe-5.0.0.hdt'
    HPO_FILENAME = 'hp.owl'

    def __init__(self, parser):
        # Parse command line.
        self.__parse_command_line(parser)

        # Defines arguments based on parser.
        self.vibe_output_dir = create_dir(self.args.output + 'vibe_output/', exist_allowed=True)

    def run(self):
        """
        Execute the runner.
        """
        try:
            # Run vibe.
            self.__run_vibe()

            # Convert vibe output for visualization.
            merge_vibe_simple_output_files(self.vibe_output_dir, f'{self.args.output}vibe.tsv')
        except FileExistsError as e:
            print(f'\nAn output file/directory already exists: {e.filename}\nExiting...')

    def __parse_command_line(self, parser):
        """
        Parsers the command line

        :param parser: the argument parser
        :type parser: ArgumentParser
        """

        # Adds runner-specific command line & parses it.
        parser.add_argument('--input', required=True, help='input tsv benchmark file')
        parser.add_argument('--output', required=True, help='directory to write output to')
        parser.add_argument('--jar', required=True, help='location of directory containing VIBE jar/data')
        parser.add_argument('--hdt', required=True, help='location of directory containing VIBE jar/data')
        parser.add_argument('--hpo', required=True, help='hpo.obo file')  # Not used but required.

        # Processes command line.
        try:
            self.args = parser.parse_args()

            # Validation.
            validate.file(self.args.input, '.tsv')
            self.args.output = validate.directory(self.args.output, create_if_not_exist=True)
            validate.file(self.args.jar, self.JAR_FILENAME)
            validate.file(self.args.hdt, self.HDT_FILENAME)
            validate.file(self.args.hdt + '.index.v1-1', self.HDT_FILENAME + '.index.v1-1')
            validate.file(self.args.hpo, self.HPO_FILENAME)
        except OSError as e:
            parser.error(e)

    def __run_vibe(self):
        """
        Runs VIBE for each benchmark case.
        """
        hpo_dict = SeparatedValuesFileReader.key_value_reader(self.args.input, 0, 2, values_separator=',')

        for key in hpo_dict.keys():
            print(f'Running VIBE: {key}')
            output_file = f'{self.vibe_output_dir}{key}.tsv'

            hpo_arguments = convert_list_to_arguments_with_same_key(hpo_dict.get(key), '-p')

            call(f'java -jar {self.args.jar} -t {self.args.hdt} {hpo_arguments} '
                 f'-o {output_file} -l -w {self.args.hpo}', shell=True)


def main(parser):
    VibeRunner5_0(parser).run()


if __name__ == '__main__':
    main(BiobesuParser())
