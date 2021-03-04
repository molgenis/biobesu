#!/user/bin/env python3

from unittest.mock import patch
from unittest.mock import mock_open
from biobesu.helper import converters

class TestPhenotypeConverter:
    # Snippet from hpo.obo file.
    hpo_obo = """format-version: 1.2
data-version: releases/2018-03-08

[Term]
id: HP:0000015
name: Bladder diverticulum
def: "Diverticulum (sac or pouch) in the wall of the urinary bladder." [HPO:probinson]
synonym: "Bladder diverticula" EXACT [HPO:skoehler]
xref: MSH:C562406
xref: SNOMEDCT_US:197866008
xref: UMLS:C0156273
is_a: HP:0025487 ! Abnormality of bladder morphology

[Term]
id: HP:0000008
name: Abnormality of female internal genitalia
def: "An abnormality of the female internal genitalia." [HPO:probinson]
xref: UMLS:C4025900
is_a: HP:0000812 ! Abnormal internal genitalia
is_a: HP:0010460 ! Abnormality of the female genitalia
"""

    @patch("builtins.open", new_callable=mock_open, read_data=hpo_obo)
    def test_id_to_symbol(self, mock_open):
        converter = converters.PhenotypeConverter("/path/to/file")

        hpo_ids = ["HP:0000008", "HP:0000015"]
        expected_output = (["Abnormality of female internal genitalia", "Bladder diverticulum"], set())
        actual_output = converter.id_to_name(hpo_ids)

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

    @patch("builtins.open", new_callable=mock_open, read_data=gene_info_file)
    def test_id_to_symbol_single(self, mock_open):
        converter = converters.GeneConverter("path/to/file")

        input_data = '9'
        expected_output = 'NAT1'
        actual_output = converter.id_to_symbol(input_data)

        assert actual_output == expected_output


    @patch("builtins.open", new_callable=mock_open, read_data=gene_info_file)
    def test_id_to_symbol_list(self, mock_open):
        converter = converters.GeneConverter("/path/to/file")

        input_data = ['10', '3']
        expected_output = (['NAT2', 'A2MP1'], set())
        actual_output = converter.id_to_symbol(input_data)

        assert actual_output == expected_output


    @patch("builtins.open", new_callable=mock_open, read_data=gene_info_file)
    def test_id_to_symbol_list_with_missing(self, mock_open):
        converter = converters.GeneConverter("/path/to/file")

        input_data = ['10', '3', '14']
        expected_output = (['NAT2', 'A2MP1'], set(('14',)))
        actual_output = converter.id_to_symbol(input_data)

        assert actual_output == expected_output