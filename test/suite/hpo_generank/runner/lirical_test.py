#!/user/bin/env python3

from biobesu.suite.hpo_generank.runner.lirical import __extract_fields_from_lirical_data


def test_lirical_file_digestion():
    input_string = ['! LIRICAL line 1\n',
                    '! LIRICAL line 2\n',
                    'rank\tdiseaseName\tdiseaseCurie\tpretestprob\tposttestprob\tcompositeLR\tentrezGeneId\tvariants\n',
                    '10\tMYDISEASE 12; ABC1\tOMIM:123456\t1/7987\t2,00%\t111,897\tn/a\tn/a\n',
                    '200\ta Syndrome\tOMIM:848484\t1/7987\t0,00%\t0\tn/a\tn/a\n',
                    '450\tJust something more; BDBS5\tOMIM:112358\t1/7987\t0,00%\t0\tn/a\tn/a\n']

    expected_output = (['ABC1', 'BDBS5'],['123456', '848484', '112358'])
    actual_output = __extract_fields_from_lirical_data(input_string)

    assert actual_output == expected_output
