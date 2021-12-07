from unittest.mock import patch, mock_open

from biobesu.suite.hpo_generank.runner import phenotype_to_genes

phenotype_to_genes_file = '''#Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol<tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
HP:0000002	Abnormality of body height	100151683	RNU4ATAC		orphadata	ORPHA:353298
HP:0000002	Abnormality of body height	2304	FOXE1		orphadata	ORPHA:95713
HP:0000002	Abnormality of body height	7227	TRPS1	-	mim2gene	OMIM:190350
HP:0001647	Bicuspid aortic valve	4313	MMP2		orphadata	ORPHA:371428
HP:0001647	Bicuspid aortic valve	4089	SMAD4		orphadata	ORPHA:91387
HP:0001648	Cor pulmonale	51776	MAP3K20		orphadata	ORPHA:2020
HP:0001648	Cor pulmonale	7169	TPM2		orphadata	ORPHA:2020
'''


@patch('builtins.open', new_callable=mock_open, read_data=phenotype_to_genes_file)
def test_data_file_loader(mock_open):
    expected_output = {'HP:0000002': ['100151683', '2304', '7227'],
                       'HP:0001647': ['4313', '4089'],
                       'HP:0001648': ['51776', '7169']}
    actual_output = phenotype_to_genes.__load_data('')

    assert actual_output == expected_output


def test_case_digestion():
    hpo2genes = {'HP:0000002': ['100151683', '2304', '7227'],
                 'HP:0001647': ['4313', '4089'],
                 'HP:0001648': ['51776', '7169']}
    hpos = ['HP:0001648', 'HP:0000002']

    expected_output = ['100151683', '2304', '7227', '51776', '7169']
    actual_output = phenotype_to_genes.__process_input_case(hpos, hpo2genes)

    assert actual_output == expected_output
