#!/user/bin/env python3

from biobesu.suite.vibe_versions.helper import converters


def test_hpo_string_to_arguments():
    input_list = ['0123456', '6543210']

    expected_output = '-p hp:0123456 -p hp:6543210'
    actual_output = converters.list_to_vibe_arguments(input_list, '-p')

    assert actual_output == expected_output


def test_omim_string_to_arguments():
    input_list = ['012345', '543210']

    expected_output = '-m omim:012345 -m omim:543210'
    actual_output = converters.list_to_vibe_arguments(input_list, '-m')

    assert actual_output == expected_output
