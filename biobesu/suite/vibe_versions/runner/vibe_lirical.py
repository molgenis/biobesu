#!/user/bin/env python3

from subprocess import call
from os import listdir
from biobesu.helper import validate
from biobesu.suite.hpo_generank.runner.lirical import __generate_phenopacket_files
from biobesu.suite.hpo_generank.runner.lirical import __run_lirical
from biobesu.helper.generic import create_dir
from biobesu.helper.readers import SeparatedValuesFileReader
from biobesu.suite.vibe_versions.helper.converters import convert_list_to_arguments_with_same_key
from biobesu.suite.vibe_versions.helper.converters import merge_vibe_simple_output_files

# Used only for docstring
from argparse import ArgumentParser
from typing import TextIO


def main(parser):
    args = __parse_command_line(parser)
    try:
        # Repeat first 2 steps of lirical runner from hpo_generank to generate LIRICAL results.
        # If Lirical will be used in actual release, a better implementation solution might be chosen.
        phenopackets_dir = __generate_phenopacket_files(args)
        lirical_output_dir = __run_lirical(args, phenopackets_dir)

        # Extract OMIMs with score > 0.
        lirical_omims_file = __extract_from_lirical_output(args, lirical_output_dir)

        # Run vibe.
        vibe_output_dir = __run_vibe(args, lirical_omims_file)

        # Convert vibe output for visualization.
        merge_vibe_simple_output_files(vibe_output_dir, args.output + 'vibe_lirical.tsv')
    except FileExistsError as e:
        print(f'\nAn output file/directory already exists: {e.filename}\nExiting...')


def __parse_command_line(parser):
    """
    Parsers the command line

    :param parser: the argument parser
    :type parser: ArgumentParser
    :return: the parsed arguments
    :rtype:
    """

    # Adds runner-specific command line.
    parser.add_argument('--input', required=True, help='input tsv benchmark file')
    parser.add_argument('--output', required=True, help='directory to write output to')
    parser.add_argument('--hpo', required=True, help='hpo.obo file')
    parser.add_argument('--lirical_jar', required=True, help='location of LIRICAL .jar file')
    parser.add_argument('--lirical_data', required=True, help='directory containing data needed by lirical')
    parser.add_argument('--vibe_jar', required=True, help='location of VIBE .jar file')
    parser.add_argument('--vibe_hdt', required=True, help='location of VIBE .hdt file')

    # Processes command line.
    try:
        args = parser.parse_args()

        # General validation.
        validate.file(args.input, '.tsv')
        args.output = validate.directory(args.output, create_if_not_exist=True)
        validate.file(args.hpo, '.obo')

        # Lirical validation.
        validate.file(args.lirical_jar, '.jar')
        args.lirical_data = validate.directory(args.lirical_data)
        validate.file(args.lirical_data + 'Homo_sapiens_gene_info.gz')
        validate.file(args.lirical_data + 'hp.obo')
        validate.file(args.lirical_data + 'mim2gene_medgen')
        validate.file(args.lirical_data + 'phenotype.hpoa')

        # Vibe validation.
        validate.file(args.vibe_jar, '.jar')
        validate.file(args.vibe_hdt, '.hdt')
        validate.file(args.vibe_hdt + '.index.v1-1', '.hdt.index.v1-1')

        # Quickfix for using args as input in hpo_generank runner lirical.
        args.jar = args.lirical_jar

    except OSError as e:
        parser.error(e)

    return args


def __extract_from_lirical_output(args, lirical_output_dir):
    """
    Extracts the relevant information from the LIRICAL output.

    :param args: the parsed arguments
    :param lirical_output_dir: the directory containing the LIRICAL output
    :type lirical_output_dir: str
    :return: file path to the omim file
    :rtype: str
    """

    extract_dir = create_dir(args.output + 'lirical_extraction/')
    lirical_omims_file = extract_dir + 'lirical_omim.tsv'

    # Omim file writer.
    with open(lirical_omims_file, 'x') as omim_writer:  # Requires creating a new file.
        omim_writer.write('id\tomims')

        # Process input files.
        for file in listdir(lirical_output_dir):
            # Generate ID column.
            id_value = file.rstrip('.tsv').split('/')[-1]
            id_column = f'\n{id_value}\t'
            omim_writer.write(id_column)

            # Create/write omim column.
            with open(lirical_output_dir + file) as input_file:
                omims = __extract_fields_from_lirical_data(input_file)
                omim_writer.write(','.join(omims))

    return lirical_omims_file


def __extract_fields_from_lirical_data(file_data):
    """
    Extracts the omim codes from an opened file.

    :param file_data: the opened file (or list of strings representing the file)
    :type file_data: TextIO | list[str]
    :return: the found omim codes
    :rtype: list[str]
    """

    omims = []
    header = True

    # Goes through all files (test cases).
    for line in file_data:
        # Skip lirical lines.
        if line.startswith('!'):
            continue

        # Skip header.
        if header:
            header = False
            continue

        line_splits = line.split('\t')

        # Return OMIMs with a compositeLR > 0.
        if float(line_splits[5].replace('.', '').replace(',', '.')) > 0:
            if line_splits[2].startswith('OMIM'):
                omims.append(line_splits[2])

    return omims


def __run_vibe(args, lirical_omims_file):
    vibe_output_dir = create_dir(args.output + 'vibe_output/')

    hpo_dict = SeparatedValuesFileReader.key_value_reader(args.input, 0, 2, values_separator=',')
    omim_dict = SeparatedValuesFileReader.key_value_reader(lirical_omims_file, 0, 1, values_separator=',')

    for key in hpo_dict.keys():
        output_file = f'{vibe_output_dir}{key}.tsv'

        hpo_arguments = convert_list_to_arguments_with_same_key(hpo_dict.get(key), '-p')
        omim_arguments = convert_list_to_arguments_with_same_key(omim_dict.get(key), '-m')

        call(f'java -jar {args.vibe_jar} -t {args.vibe_hdt} {hpo_arguments} {omim_arguments} '
             f'-o {output_file} -l', shell=True)

    return vibe_output_dir
