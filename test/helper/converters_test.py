#!/user/bin/env python3

from unittest.mock import patch
from unittest.mock import mock_open
from biobesu.helper import converters
from re import sub


class TestPhenotypeConverter:
    # Snippet from hpo.obo file:
    # Kept first 2 lines with version/date.
    # A few HPO terms with differing (amount of) keys. Skipped 1-7 when looking for test HPOs (1 is root,
    # 2-3 skipped due to containing long strings, 4-7 are inheritance modes).
    hpo_obo = """format-version: 1.2
data-version: releases/2018-03-08

[Term]
id: HP:0000008
name: Abnormality of female internal genitalia
def: "An abnormality of the female internal genitalia." [HPO:probinson]
xref: UMLS:C4025900
is_a: HP:0000812 ! Abnormal internal genitalia
is_a: HP:0010460 ! Abnormality of the female genitalia

[Term]
id: HP:0000015
name: Bladder diverticulum
def: "Diverticulum (sac or pouch) in the wall of the urinary bladder." [HPO:probinson]
synonym: "Bladder diverticula" EXACT [HPO:skoehler]
xref: MSH:C562406
xref: SNOMEDCT_US:197866008
xref: UMLS:C0156273
is_a: HP:0025487 ! Abnormality of bladder morphology

"""

    @patch('builtins.open', new_callable=mock_open, read_data=hpo_obo)
    def test_id_to_symbol(self, mock_open):
        converter = converters.PhenotypeConverter('/path/to/file')

        hpo_ids = ['HP:0000008', 'HP:0000015']
        expected_output = (['Abnormality of female internal genitalia', 'Bladder diverticulum'], set())
        actual_output = converter.id_to_name(hpo_ids)

        assert actual_output == expected_output

    @patch('builtins.open', new_callable=mock_open, read_data=hpo_obo)
    def test_symbol_to_id(self, mock_open):
        converter = converters.PhenotypeConverter('/path/to/file')

        hpo_names = ['Abnormality of female internal genitalia', 'Bladder diverticulum']
        expected_output = (['HP:0000008', 'HP:0000015'], set())
        actual_output = converter.name_to_id(hpo_names)

        assert actual_output == expected_output

    @patch('builtins.open', new_callable=mock_open, read_data=hpo_obo)
    def test_id_to_phenopackets(self, mock_open):
        converter = converters.PhenotypeConverter('/path/to/file')

        phenopacket_id = '01234'
        hpo_ids = ['HP:0000008', 'HP:0000015']

        # Based on https://phenopackets-schema.readthedocs.io/en/v1.1/phenopacket.html
        # Created string is empty to evade test failing due to different timestamps.
        expected_output = '{' \
            '\n\t"id": "01234",' \
            '\n\t"phenotypic_features": [' \
            '\n\t\t{' \
            '\n\t\t\t"type": {' \
            '\n\t\t\t\t"id": "HP:0000008",' \
            '\n\t\t\t\t"label": "Abnormality of female internal genitalia"' \
            '\n\t\t\t}' \
            '\n\t\t},' \
            '\n\t\t{' \
            '\n\t\t\t"type": {' \
            '\n\t\t\t\t"id": "HP:0000015",' \
            '\n\t\t\t\t"label": "Bladder diverticulum"' \
            '\n\t\t\t}' \
            '\n\t\t}' \
            '\n\t],' \
            '\n\t"meta_data": {' \
            '\n\t\t"created": "",' \
            '\n\t\t"created_by": "biobesu",' \
            '\n\t\t"resources": [' \
            '\n\t\t\t{' \
            '\n\t\t\t\t"id": "hp",' \
            '\n\t\t\t\t"name": "Human Phenotype Ontology",' \
            '\n\t\t\t\t"namespacePrefix": "HP",' \
            '\n\t\t\t\t"url": "http://purl.obolibrary.org/obo/hp.owl",' \
            '\n\t\t\t\t"version": "2018-03-08",' \
            '\n\t\t\t\t"iriPrefix": "http://purl.obolibrary.org/obo/HP_"' \
            '\n\t\t\t}' \
            '\n\t\t]' \
            '\n\t}' \
            '\n}'

        actual_output = converter.id_to_phenopacket(phenopacket_id, hpo_ids)

        # Replace created date with empty string for comparison.
        actual_output = sub(r'"created": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z"', '"created": ""', actual_output)

        assert actual_output == expected_output


class TestGeneConverter:
    # Snippet from genenames.org custom download file.
    gene_info_file = """NCBI Gene ID	Approved symbol
1	A1BG
2	A2M
3	A2MP1
9	NAT1
10	NAT2
11	NATP
"""

    @patch('builtins.open', new_callable=mock_open, read_data=gene_info_file)
    def test_id_to_symbol_single(self, mock_open):
        converter = converters.GeneConverter('path/to/dir')

        input_data = '9'
        expected_output = 'NAT1'
        actual_output = converter.id_to_symbol(input_data)

        assert actual_output == expected_output

    @patch('builtins.open', new_callable=mock_open, read_data=gene_info_file)
    def test_id_to_symbol_list(self, mock_open):
        converter = converters.GeneConverter('/path/to/dir')

        input_data = ['10', '3']
        expected_output = (['NAT2', 'A2MP1'], set())
        actual_output = converter.id_to_symbol(input_data)

        assert actual_output == expected_output

    @patch('builtins.open', new_callable=mock_open, read_data=gene_info_file)
    def test_id_to_symbol_list_with_missing(self, mock_open):
        converter = converters.GeneConverter('/path/to/dir')

        input_data = ['10', '3', '14']
        expected_output = (['NAT2', 'A2MP1'], {'14'})
        actual_output = converter.id_to_symbol(input_data)

        assert actual_output == expected_output

    @patch('builtins.open', new_callable=mock_open, read_data=gene_info_file)
    def test_symbol_to_id(self, mock_open):
        converter = converters.GeneConverter('path/to/dir')

        input_data = 'NAT1'
        expected_output = '9'
        actual_output = converter.symbol_to_id(input_data)

        assert actual_output == expected_output
