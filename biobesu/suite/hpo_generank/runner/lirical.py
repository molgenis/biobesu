#!/user/bin/env python3

from subprocess import call
from os import listdir
from re import search
from biobesu.helper import validate
from biobesu.helper.generic import create_dir
from biobesu.helper.generic import eprint
from biobesu.suite.hpo_generank.helper.converters import LiricalGeneAliasConverter
from biobesu.suite.hpo_generank.helper.converters import LiricalOmimConverter
from biobesu.helper.converters import GeneConverter
from biobesu.helper.converters import PhenotypeConverter


def main(parser):
    args = __parse_command_line(parser)
    try:
        phenopackets_dir = __generate_phenopacket_files(args)
        lirical_output_dir = __run_lirical(args, phenopackets_dir)
        lirical_gene_alias_file, lirical_omims_file = __extract_from_lirical_output(args, lirical_output_dir)
        __convert_lirical_extractions(args, lirical_gene_alias_file, lirical_omims_file)
    except FileExistsError as e:
        print("\nAn output file/directory already exists: " + e.filename + "\nExiting...")


def __parse_command_line(parser):
    # Adds runner-specific command line.
    parser.add_argument("--jar", required=True, help="location of LIRICAL .jar file")
    parser.add_argument("--hpo", required=True, help="hpo.obo file")
    parser.add_argument("--input", required=True, help="input tsv benchmark file")
    parser.add_argument("--output", required=True, help="directory to write output to")
    parser.add_argument("--lirical_data", required=True, help="directory containing data needed by lirical")
    parser.add_argument("--runner_data", required=True, help="directory that can used to store needed data")

    # Processes command line.
    try:
        args = parser.parse_args()
        validate.file(args.input, ".tsv")
        validate.file(args.hpo, ".obo")
        validate.file(args.jar, ".jar")
        args.output = validate.directory(args.output)

        args.lirical_data = validate.directory(args.lirical_data)
        validate.file(args.lirical_data + "Homo_sapiens_gene_info.gz")
        validate.file(args.lirical_data + "hp.obo")
        validate.file(args.lirical_data + "mim2gene_medgen")
        validate.file(args.lirical_data + "phenotype.hpoa")
    except OSError as e:
        parser.error(e)

    return args


def __generate_phenopacket_files(args):
    phenopackets_dir = create_dir(args.output + "phenopackets/")
    converter = PhenotypeConverter(args.hpo)

    # Digests the benchmark cases.
    for i, line in enumerate(open(args.input)):
        # Skips first line (header).
        if i == 0:
            continue

        # Splits the columns.
        line = line.rstrip().split('\t')

        # Retrieve converted data.
        output_string = converter.id_to_phenopacket(line[0], line[2].split(','))

        # Write output.
        file_writer = open(phenopackets_dir + line[0] + '.json', 'w')
        file_writer.write(output_string)
        file_writer.flush()
        file_writer.close()

    return phenopackets_dir


def __run_lirical(args, phenopackets_dir):
    lirical_output_dir = create_dir(args.output + "lirical_output/")

    # Run tool for each input file.
    for file in listdir(phenopackets_dir):
        file_path = phenopackets_dir + file
        file_id = file.rstrip(".json").split('/')[-1]
        call("java -jar " + args.jar + " phenopacket -p " + file_path + " -o " + lirical_output_dir + " -x " + file_id +
             " -d " + args.lirical_data + " --tsv", shell=True)

    return lirical_output_dir


def __extract_from_lirical_output(args, lirical_output_dir):
    extract_dir = create_dir(args.output + "lirical_extraction/")
    lirical_gene_alias_file = extract_dir + "lirical_gene_alias.tsv"
    lirical_omims_file = extract_dir + "lirical_omim.tsv"

    # Gene alias file writer.
    with open(lirical_gene_alias_file, 'x') as alias_writer:  # Requires creating a new file.
        alias_writer.write("id\tgene_aliases")

        # Omim file writer.
        with open(lirical_omims_file, 'x') as omim_writer:  # Requires creating a new file.
            omim_writer.write("id\tomims")

            # Process input files.
            for file in listdir(lirical_output_dir):
                # Generate ID column.
                id_column = "\n{}\t".format(file.rstrip(".tsv").split('/')[-1])
                alias_writer.write(id_column)
                omim_writer.write(id_column)

                # Create/write genes column.
                with open(lirical_output_dir + file) as input_file:
                    genes, omims = __extract_fields_from_lirical_data(input_file)
                    alias_writer.write(','.join(genes))
                    omim_writer.write(','.join(omims))

    return lirical_gene_alias_file, lirical_omims_file


def __extract_fields_from_lirical_data(file_data):
    genes = []
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

        gene_alias = search(r'\t[\w, ]+; ([\w]+)', line)
        if gene_alias is not None:
            genes.append(gene_alias[1])
        omims.append(line.split('\t')[2].split(':')[1])

    return genes, omims


def __convert_lirical_extractions(args, lirical_gene_alias_file, lirical_omims_file):
    conversion_dir = create_dir(args.output + "lirical_conversion/")
    converted_gene_alias_file = conversion_dir + "lirical_gene_alias_converted.tsv"
    converted_omim_intermediate = conversion_dir + "lirical_omim_gene_id.tsv"
    converted_omim_file = conversion_dir + "lirical_omim_converted.tsv"
    final_header = "id\tgene_symbol\n"

    # Route 1 to gene symbols.
    print("Retrieve genes through gene aliases...")
    missing = __convert_lirical_output_digest(LiricalGeneAliasConverter(args.lirical_data + "Homo_sapiens_gene_info.gz").alias_to_gene_symbol,
                                              lirical_gene_alias_file, converted_gene_alias_file, final_header)
    eprint("Failed to convert these gene aliases to gene symbols: {}\n".format(missing))

    # Route 2 to gene symbols.
    print("Retrieve genes through OMIM...")
    missing = __convert_lirical_output_digest(LiricalOmimConverter(args.lirical_data + "mim2gene_medgen").omim_to_gene_id,
                                              lirical_omims_file, converted_omim_intermediate, "id\tgene_id\n")
    eprint("Failed to convert these OMIMs to gene IDs: {}\n".format(missing))

    missing = __convert_lirical_output_digest(GeneConverter(args.runner_data).id_to_symbol,
                                              converted_omim_intermediate, converted_omim_file, final_header)
    eprint("Failed to convert these gene IDs to gene symbols: {}\n".format(missing))


def __convert_lirical_output_digest(convert_method, input_file, output_file, output_file_header):
    # Set for collecting aliases without a symbol.
    all_missing = set()

    with open(output_file, 'x') as file_writer:  # Requires creating a new file.
        # Write header.
        file_writer.write(output_file_header)

        # Process input file.
        with open(input_file) as file_reader:
            for i, line in enumerate(file_reader):
                # Skip header.
                if i == 0:
                    continue

                # Process line.
                line = line.rstrip().split('\t')
                converted, missing = convert_method(line[1].split(','), include_na=False)

                # Digest results.
                file_writer.write(line[0] + '\t' + ','.join(converted) + '\n')
                all_missing.update(missing)

    return missing
