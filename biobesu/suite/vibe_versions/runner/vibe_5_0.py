#!/user/bin/env python3

from subprocess import call
from biobesu.helper import validate
from biobesu.helper.generic import create_dir
from biobesu.helper.readers import SeparatedValuesFileReader
from biobesu.helper.downloaders import bytes_file_downloader
from biobesu.helper.downloaders import archive_downloader
from biobesu.suite.vibe_versions.helper.converters import list_to_vibe_arguments
from biobesu.suite.vibe_versions.helper.converters import merge_vibe_simple_output_files
from biobesu.helper.argument_parser import BiobesuParser

# Used only for docstring
from argparse import ArgumentParser


class VibeRunner5_0:
    VIBE_FILE = 'vibe-with-dependencies-5.0.3.jar'
    VIBE_DOWNLOAD = f'https://github.com/molgenis/vibe/releases/download/vibe-5.0.3/{VIBE_FILE}'
    DATABASE_FILE = 'vibe-5.0.0-hdt/vibe-5.0.0.hdt'
    DATABASE_ARCHIVE = 'vibe-5.0.0-hdt.tar.gz'
    DATABASE_DOWNLOAD = f'https://downloads.molgeniscloud.org/downloads/vibe/{DATABASE_ARCHIVE}'
    HPO_FILE = 'hp.owl'
    HPO_DOWNLOAD = f'https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/2f6309173883d5d342849388c74bd986a2c0092c/{HPO_FILE}'

    def __init__(self, parser):
        # Parse command line.
        self.__parse_command_line(parser)

        # Defines arguments based on parser.
        self.vibe_output_dir = create_dir(self.args.output + 'vibe_output/')

    def run(self):
        """
        Execute the runner.
        """
        try:
            # Download/validate resources.
            if self.args.download:
                self.__download_vibe()
                self.__validate_downloads()

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
        parser.add_argument('--hpo', required=True, help='hpo.obo file')  # not used but required
        parser.add_argument('--data', required=True, help='location of directory containing VIBE jar/data')
        parser.add_argument('--download', action='store_true', help='indicate data should be downloaded')

        # Processes command line.
        try:
            self.args = parser.parse_args()

            # Validation.
            validate.file(self.args.input, '.tsv')
            self.args.output = validate.directory(self.args.output)
            validate.file(self.args.hpo, '.owl')

            # Validates data if not downloaded.
            if not self.args.download:
                self.__validate_downloads()
        except OSError as e:
            parser.error(e)

    def __download_vibe(self):
        """
        Downloads the data needed for VIBE.
        """
        bytes_file_downloader(self.VIBE_DOWNLOAD, self.args.data)
        archive_downloader(self.DATABASE_DOWNLOAD, self.args.data)
        bytes_file_downloader(self.HPO_DOWNLOAD, self.args.data)

    def __validate_downloads(self):
        """
        Validates the data needed for VIBE.
        """
        validate.file(self.args.data + self.VIBE_FILE, '.jar')
        validate.file(self.args.data + self.DATABASE_FILE, '.hdt')
        validate.file(self.args.data + self.DATABASE_FILE + '.index.v1-1', '.hdt.index.v1-1')
        validate.file(self.args.data + self.HPO_FILE, '.owl')

    def __run_vibe(self):
        """
        Runs VIBE for each benchmark case.
        """
        hpo_dict = SeparatedValuesFileReader.key_value_reader(self.args.input, 0, 2, values_separator=',')

        for key in hpo_dict.keys():
            print(f'Running VIBE: {key}')
            output_file = f'{self.vibe_output_dir}{key}.tsv'

            hpo_arguments = list_to_vibe_arguments(hpo_dict.get(key), '-p')

            call(f'java -jar {self.args.data}{self.VIBE_FILE} -t {self.args.data}{self.DATABASE_FILE} {hpo_arguments} '
                 f'-o {output_file} -l -w {self.args.data}{self.HPO_FILE}', shell=True)


def main(parser):
    runner = VibeRunner5_0(parser)
    runner.run()


if __name__ == '__main__':
    main(BiobesuParser())
