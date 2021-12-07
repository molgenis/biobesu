#!/user/bin/env python3

from biobesu.helper import validate
from biobesu.helper.argument_parser import BiobesuParser
from biobesu.suite.hpo_generank.runner_config import RunnerConfig


def main(parser):
    args = __parse_command_line(parser)
    hpo2gene = __load_data(args.data)
    __generate_results(args.input, args.output, hpo2gene)


def __parse_command_line(parser):
    """
    Parsers the command line

    :param parser: the argument parser
    :type parser: ArgumentParser
    :return: the parsed arguments
    :rtype:
    """

    # Adds runner-specific command line.
    parser.add_argument('--data', required=True, help='HPO phenotype_to_genes file (as downloaded from https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/)')
    parser.add_argument('--input', required=True, help='input tsv benchmark file')
    parser.add_argument('--output', required=True, help='file to write output to')

    # Processes command line.
    try:
        args = parser.parse_args()
        validate.file(args.data, '.tsv')
        validate.file(args.input, '.tsv')
        validate.directory(args.output, writable=True, create_if_not_exist=True,
                           remove_filename=True)
        validate.filename(args.output)
    except OSError as e:
        parser.error(e)

    return args


def __load_data(filepath):
    hpo2gene = {}

    with open(filepath) as reader:
        for line in reader:
            # Skips header line.
            if line.startswith('#'):
                continue

            line_splits = line.split('\t')
            hpo = line_splits[0]
            gene = line_splits[2]

            if hpo not in hpo2gene.keys():
                hpo2gene[hpo] = []
            # Ensures same order is kept (in contrary to set).
            if gene not in hpo2gene.get(hpo):
                hpo2gene.get(hpo).append(gene)

    return hpo2gene


def __generate_results(infile, outfile, hpo2gene):
    with open(outfile, 'w') as writer:
        writer.write(RunnerConfig.OUTPUT_HEADER)
        with open(infile) as reader:
            for i, line in enumerate(reader):
                # Skip header line.
                if i == 0:
                    continue

                # Splits the columns.
                line = line.rstrip().split('\t')
                case_id = line[0]
                hpos = line[2].split(',')
                found_genes = __process_input_case(hpos, hpo2gene)
                writer.write(case_id + '\t' + ','.join(found_genes) + '\n')


def __process_input_case(phenotypes, hpo2gene):
    # Stores all genes for the input phenotypes.
    found_genes = []

    # Ensures order of input phenotypes does not influence results.
    if type(phenotypes) is list:
        phenotypes.sort()

    # Processes phenotypes.
    for phenotype in phenotypes:
        hpo_genes = hpo2gene.get(phenotype)
        if hpo_genes is not None:
            # Keeps order of genes and ensures gene is only added once.
            for hpo_gene in hpo_genes:
                if hpo_gene not in found_genes:
                    found_genes.append(hpo_gene)

    return found_genes


if __name__ == '__main__':
    main(BiobesuParser())
