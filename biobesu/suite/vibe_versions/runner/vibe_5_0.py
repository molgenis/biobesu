#!/user/bin/env python3
from os.path import isfile
from subprocess import call
from time import perf_counter
from biobesu.helper import validate
from biobesu.helper.generic import create_dir
from biobesu.helper.readers import SeparatedValuesFileReader
from biobesu.suite.vibe_versions.helper.converters import \
    convert_list_to_arguments_with_same_key
from biobesu.suite.vibe_versions.helper.converters import \
    merge_vibe_simple_output_files
from biobesu.helper.argument_parser import BiobesuParser

# Used only for docstring
from argparse import ArgumentParser


class VibeRunner5_0:
    JAR_FILENAME = 'vibe-with-dependencies-5.0.3.jar'
    HDT_FILENAME = 'vibe-5.0.0.hdt'
    HPO_FILENAME = '.owl'  # Given owl file does not matter as it is not used.
    OUTPUT_SUBDIR = '5.0/'
    FINAL_OUTPUT_FILE = 'vibe_5.0.3.tsv'

    def __init__(self, parser):
        # Parse command line.
        self.__parse_command_line(parser)

        # Defines arguments based on parser.
        self.vibe_output_dir = create_dir(self.args.output + 'vibe_output/',
                                          exist_allowed=True)
        self.times_output_file = f'{self.args.output}times.tsv'

    def run(self):
        """
        Execute the runner.
        """
        try:
            # Run vibe.
            self.__run_benchmark()

            # Convert vibe output for visualization.
            merge_vibe_simple_output_files(self.vibe_output_dir,
                                           f'{self.args.output}'
                                           f'{self.FINAL_OUTPUT_FILE}')
        except FileExistsError as e:
            print(f'\nAn output file/directory already exists: '
                  f'{e.filename}\nExiting...')

    def __parse_command_line(self, parser):
        """
        Parsers the command line

        :param parser: the argument parser
        :type parser: ArgumentParser
        """

        # Adds runner-specific command line & parses it.
        parser.add_argument('-i', '--input', required=True,
                            help='input tsv benchmark file')
        parser.add_argument('-o', '--output', required=True,
                            help='directory to write output to')
        parser.add_argument('-j', '--jar', required=True,
                            help='directory containing VIBE jar')
        parser.add_argument('-d', '--hdt', required=True,
                            help='path to HDT file')
        parser.add_argument('-p', '--hpo', required=True,
                            help='hpo.owl file')  # Not used but required.

        # Processes command line.
        try:
            self.args = parser.parse_args()

            # Validation.
            validate.file(self.args.input, '.tsv')
            self.args.output = validate.directory(self.args.output,
                                                  create_if_not_exist=True) + \
                               self.OUTPUT_SUBDIR
            validate.file(self.args.jar, self.JAR_FILENAME)
            validate.file(self.args.hdt, self.HDT_FILENAME)
            validate.file(self.args.hdt + '.index.v1-1',
                          self.HDT_FILENAME + '.index.v1-1')
            validate.file(self.args.hpo, self.HPO_FILENAME)
        except OSError as e:
            parser.error(e)

    def __run_benchmark(self):
        """
        Runs VIBE for each benchmark case.
        """
        # Generates dict from input file: {id:[hpo, hpo]}.
        hpo_dict = SeparatedValuesFileReader. \
            key_value_reader(self.args.input, 0, 2, values_separator=',')

        # Prepares times file.
        time_file_add_header = False
        if not isfile(self.times_output_file):
            time_file_add_header = True

        # Opens times file.
        with open(self.times_output_file, 'a') as times_writer:
            # Adds header if file did not already exist.
            if time_file_add_header:
                times_writer.write('id\ttime (%H:%M:%S.%f)\n')
            # Processes all HPO input sets.
            for key in hpo_dict.keys():
                print(f'Running VIBE: {key}')
                self.__run_vibe(times_writer, key, hpo_dict.get(key))

    def __run_vibe(self, times_writer, run_id, hpo_list):
        """
        Executes a single VIBE run.

        :param run_id: the identifier of the run
        :type run_id: str
        :param hpo_list: a list with all HPO
        """
        output_file = f'{self.vibe_output_dir}{run_id}.tsv'
        if isfile(output_file):
            print(f'{output_file} already exits. Skipping...')
            return

        hpo_arguments = convert_list_to_arguments_with_same_key(hpo_list, '-p')

        time_start = perf_counter()

        call(f'java -jar {self.args.jar} -l '
             f'{hpo_arguments} '
             f'-t {self.args.hdt} '
             f'-o {output_file} '
             f'-w {self.args.hpo}',
             shell=True)

        time_elapsed = perf_counter() - time_start
        times_writer.write(f'{run_id}\t{time_elapsed}s\n')


def main(parser):
    VibeRunner5_0(parser).run()


if __name__ == '__main__':
    main(BiobesuParser())
