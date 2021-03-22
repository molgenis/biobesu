#!/user/bin/env python3

from biobesu.helper.converters import Converter
import gzip


class LiricalGeneAliasConverter(Converter):
    """
    Converts gene aliases to gene symbols through the LIRICAL supplied "Homo_sapiens_gene_info.gz" file.
    """

    def __init__(self, gene_info_file):
        self.gene_info_dict = self.__read_file(gene_info_file)

    def __read_file(self, file_path):
        gene_info_dict = {}

        with gzip.open(file_path, 'rt') as file:
            for line in file:
                line = line.split('\t')
                gene_symbol = line[2]
                aliases = line[4]
                aliases = aliases.split('|')

                for alias in aliases:
                    gene_info_dict[alias] = gene_symbol

        return gene_info_dict

    def alias_to_gene_symbol(self, gene_aliases, include_na=False):
        """
        Convert a (list of) gene alias(es) to its/their gene symbol(s).

        :param gene_aliases: (list of) gene alias(es) to convert
        :type gene_aliases: str | list[str]
        :param include_na:  replace IDs with no match with "NA" in the returned output
        :type include_na: bool
        :return (str, None or tuple): the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """
        
        return self.key_to_value(gene_aliases, self.gene_info_dict, include_na)


class LiricalOmimConverter(Converter):
    """
    Converts OMIM to gene IDs through the LIRICAL supplied "mim2gene_medgen" file.
    """

    def __init__(self, mim2gene_medgen_file):
        self.omim_dict = self.__read_file(mim2gene_medgen_file)

    def __read_file(self, file_path):
        omim_dict = {}

        with open(file_path) as file:
            for line in file:
                line = line.split('\t')
                if line[1] != '-':
                    omim_dict[line[0]] = line[1]

        return omim_dict

    def omim_to_gene_id(self, omims, include_na=False):
        """
        Convert a (list of) omim(s) to its/their gene ID(s).

        :param omims: (list of) omim(s) to convert
        :type omims: str | list[str]
        :param include_na:  replace IDs with no match with "NA" in the returned output
        :type include_na: bool
        :return (str, None or tuple): the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """

        return self.key_to_value(omims, self.omim_dict, include_na)
