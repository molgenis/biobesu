#!/user/bin/env python3

from datetime import datetime
from biobesu.helper import validate
from json import dumps
import requests
from biobesu.helper.error import FileContentError


class Converter:
    """
    Superclass for converters that contains general methods.
    """

    @staticmethod
    def key_to_value(keys, conversion_dict, include_na=False):
        """
        Converts a key to a value using a conversion dict.

        If keys is a String, a String is returned containing the converted value or None if no value was found.

        If keys is a list, a tuple is returned with as first element a list with the found values (and NAs if
        include_na=true), and as second element a set with strings for which no conversion value was found.

        If include_na==True, then the returned list will contain an "NA" in the position of an item for which no
        conversion value could be found. Otherwise, these are simply left out.

        :param keys: the item(s) that need to be converted
        :type keys: str | list[str]
        :param conversion_dict: dict to use for conversion
        :type conversion_dict: dict[str,str]
        :param include_na: whether missing results should be returned in the output as "NA"
        :type include_na: bool
        :return: the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """

        if type(keys) is list:
            values = []
            missing = set()
            for key in keys:
                try:
                    values.append(conversion_dict[key])
                except KeyError:
                    if include_na:
                        values.append('NA')
                    missing.add(key)

            return values, missing

        else:
            try:
                return conversion_dict[keys]
            except KeyError:
                return None


class PhenotypeConverter(Converter):
    """
    Converter for phenotype data.
    """

    def __init__(self, hpo_obo):
        # Defines dictionaries for fast retrieval.
        self.names_by_id = {}
        self.id_by_names = {}

        # Stores hpo obo relevant information.
        self.hpo_obo_version = ''

        # Processes hpo obo file.
        self.read_hpo_obo(hpo_obo)

    def read_hpo_obo(self, hpo_obo):
        """
        Read the HPO obo file used as source for conversion.

        :param hpo_obo: path to hpo_obo file
        :type hpo_obo: str
        """

        # Match terms for header.
        match_version = 'data-version:'

        # Match terms for phenotypes.
        match_term = '[Term]'
        match_id = 'id: '
        match_name = 'name: '

        # Initializes variables.
        hpo_id = None
        hpo_name = None
        added = False

        # Goes through the .obo file.
        with open(hpo_obo) as file:
            for line in file:
                if line.startswith(match_version):
                    self.hpo_obo_version = line.split('/')[1].rstrip()
                # Resets id and name for new phenotype.
                if line.startswith(match_term):
                    hpo_id = None
                    hpo_name = None
                    added = False
                # Once a phenotype is added, skips lines until next term.
                elif added is True:
                    continue
                # Sets id/name when found.
                elif line.startswith(match_id):
                    hpo_id = line.lstrip(match_id).strip()
                elif line.startswith(match_name):
                    hpo_name = line.lstrip(match_name).strip()

                # If a combination of an id and a name/synonym is stored, saves it to the dictionaries.
                # Afterwards, reset id to None so that next lines will be ignored till the next phenotype.
                if hpo_id is not None and hpo_name is not None:
                    self.names_by_id[hpo_id] = hpo_name
                    self.id_by_names[hpo_name] = hpo_id
                    added = True

    def id_to_name(self, hpo_ids, include_na=False):
        """
        Convert a (list of) phenotype ID(s) to its/their name.

        :param hpo_ids: (list of) phenotype(s) to convert
        :type hpo_ids: str | list[str]
        :param include_na:  replace IDs with no match with "NA" in the returned output
        :type include_na: bool
        :return (str, None or tuple): the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """

        return self.key_to_value(hpo_ids, self.names_by_id, include_na)

    def name_to_id(self, hpo_names, include_na=False):
        """
        Convert a (list of) phenotype name(s) to its/their ID.
        :param hpo_names: (list of) phenotype(s) to convert
        :type hpo_names: str | list[str]
        :param include_na: replace IDs with no match with "NA" in the returned output
        :type include_na: bool
        :return: the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """

        return self.key_to_value(hpo_names, self.id_by_names, include_na)

    def id_to_phenopacket(self, phenopacket_id, phenotype_ids):
        """
        Convert a list of phenotype IDs to a phenopacket.
        :param phenopacket_id: the ID to be used for the phenopacket
        :type phenopacket_id str
        :param phenotype_ids: the phenotypes to convert
        :type phenotype_ids: list[str]
        :return: a JSON-formatted phenopacket string
        :rtype: str
        """

        # Create json dict with id.
        json_dict = {'id': phenopacket_id}

        # Add phenotype information to json dict.
        phenotypic_features = []
        for i, phenotype_id in enumerate(phenotype_ids):
            phenotypic_features.append({
                'type': {
                    'id': phenotype_id,
                    'label': self.names_by_id[phenotype_id]
                }
            })
        json_dict['phenotypic_features'] = phenotypic_features

        # Adds metadata to json dict.
        json_dict['meta_data'] = {
            'created': datetime.utcnow().isoformat()+'Z',
            'created_by': 'biobesu',
            'resources': [{
                'id': 'hp',
                'name': 'Human Phenotype Ontology',
                'namespacePrefix': 'HP',
                'url': 'http://purl.obolibrary.org/obo/hp.owl',
                'version': self.hpo_obo_version,
                'iriPrefix': 'http://purl.obolibrary.org/obo/HP_'
            }]
        }

        # Serializes dict to json and returns string.
        return dumps(json_dict, indent='\t')


class GeneConverter(Converter):
    """
    Converter for gene data.

    Makes use of a file that is downloaded from genenames if not already found in the given directory. If a file with
    the expected name is already present in the directory, assumes it was downloaded through this class previously.
    """

    # Download URL (ordered by gene ID).
    download_file = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_pub_eg_id&col=gd_app_sym' \
                    '&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_pub_eg_id' \
                    '&format=text&submit=submit'

    # Expected file name.
    file_name = 'gene_ids_symbols.tsv'

    # Expected header format.
    expected_file_header = 'NCBI Gene ID\tApproved symbol'

    def __init__(self, gene_file_dir):
        # The file location that needs to be loaded.
        self.gene_file = gene_file_dir + self.file_name

        # Downloads info file if not yet present in dir.
        try:
            validate.file(self.gene_file, expected_extension='.tsv')
        except OSError:
            self.__download_info_file()

        # Defines dictionaries for fast retrieval.
        self.id_by_symbol = {}
        self.symbol_by_id = {}

        # Retrieves data.
        self.__read_file()

    def __download_info_file(self):
        """
        Downloads needed conversion file and writes it the the given directory.
        """

        with requests.get(self.download_file, allow_redirects=True) as r:
            with open(self.gene_file, 'x') as file_writer:
                file_writer.write(r.content.decode('utf-8'))

    def __read_file(self):
        """
        Digests the conversion file.
        """

        # Goes through the file.
        for counter, line in enumerate(open(self.gene_file)):
            # Validates if all expected columns are present and in expected order.
            if counter == 0 and line.rstrip() != self.expected_file_header:
                raise FileContentError(f'Unexpected gene info file header.\nExpected: '
                                       f'{self.expected_file_header}\nActual: {line}')

            # Processes items.
            if counter > 0:
                line = line.rstrip().split('\t')

                # Ensures all items are of equal length after splitting.
                while len(line) < 2:
                    line.append('')

                # Clearer usage of data.
                gene_id = line[0]
                gene_symbol = line[1]

                # Adds gene to dict.
                if gene_id != '':
                    if self.id_by_symbol.get(gene_symbol) is not None:
                        raise FileContentError(f'The symbol {gene_symbol} was already assigned to {gene_id}')
                    self.id_by_symbol[gene_symbol] = gene_id
                    self.symbol_by_id[gene_id] = gene_symbol

    def id_to_symbol(self, gene_ids, include_na=False):
        """
        Convert a (list of) gene id(s) to its/their symbol.
        :param gene_ids: (list of) gene(s) to convert
        :type gene_ids: str | list[str]
        :param include_na: replace IDs with no match with "NA" in the returned output
        :type include_na: bool
        :return: the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """

        return self.key_to_value(gene_ids, self.symbol_by_id, include_na)

    def symbol_to_id(self, gene_symbols, include_na=False):
        """
        Convert a (list of) gene symbol(s) to its/their ID.
        :param gene_symbols: (list of) gene(s) to convert
        :type gene_symbols: str | list[str]
        :param include_na: replace IDs with no match with "NA" in the returned output
        :type include_na: bool
        :return: the converted keys
        :rtype: str | None | tuple[list[str],set[str]]
        """

        return self.key_to_value(gene_symbols, self.id_by_symbol, include_na)