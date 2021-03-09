#!/user/bin/env python3

from unittest.mock import patch
from unittest.mock import mock_open
from io import BytesIO
from gzip import GzipFile
from biobesu.suite.hpo_generank.helper import converters


class TestLiricalGeneAliasConverter:
    # Snippet from input data. As the class expects a gzipped input file, first converts this string to a gzip
    # compressed string stored in "gene_info_file", from which the compressed data is retrieved through giving
    # "gene_info_file.getvalue()" to the mocker.
    gene_info_string = b"#tax_id\tGeneID\tSymbol\tLocusTag\tSynonyms\tdbXrefs\tchromosome\tmap_location\tdescription\ttype_of_gene\tSymbol_from_nomenclature_authority\tFull_name_from_nomenclature_authority\tNomenclature_status\tOther_designations\tModification_date\tFeature_type" \
                       b"\n9606\t1\tA1BG\t-\tA1B|ABG|GAB|HYST2477\tMIM:138670|HGNC:HGNC:5|Ensembl:ENSG00000121410\t19\t19q13.43\talpha-1-B glycoprotein\tprotein-coding\tA1BG\talpha-1-B glycoprotein\tO\talpha-1B-glycoprotein|HEL-S-163pA|epididymis secretory sperm binding protein Li 163pA\t20210203\t-" \
                       b"\n9606\t2\tA2M\t-\tA2MD|CPAMD5|FWP007|S863-7\tMIM:103950|HGNC:HGNC:7|Ensembl:ENSG00000175899\t12\t12p13.31\talpha-2-macroglobulin\tprotein-coding\tA2M\talpha-2-macroglobulin\tO\talpha-2-macroglobulin|C3 and PZP-like alpha-2-macroglobulin domain-containing protein 5|alpha-2-M\t20210220\t-"
    gene_info = BytesIO()
    compress = GzipFile(fileobj=gene_info, mode='wb')
    compress.write(gene_info_string)
    compress.close()

    @patch("builtins.open", new_callable=mock_open, read_data=gene_info.getvalue())
    def test_alias_to_gene_symbol(self, mock_open):
        converter = converters.LiricalGeneAliasConverter("/path/to/file")

        aliases = ["GAB", "CPAMD5"]
        expected_output = (["A1BG", "A2M"], set())
        actual_output = converter.alias_to_gene_symbol(aliases)

        assert actual_output == expected_output


class TestLiricalOmimConverter:
    mim2_gene = """#MIM number	GeneID	type	Source	MedGenCUI	Comment
100100	1131	phenotype	 GeneMap	C0033770	-
100200	-	phenotype	-	C4551519	-
100300	57514	phenotype	 GeneMap	C4551482	-
"""

    @patch("builtins.open", new_callable=mock_open, read_data=mim2_gene)
    def test_alias_to_gene_symbol(self, mock_open):
        converter = converters.LiricalOmimConverter("/path/to/file")

        omims = ["100300", "100100"]
        expected_output = (["57514", "1131"], set())
        actual_output = converter.omim_to_gene_id(omims)

        assert actual_output == expected_output
