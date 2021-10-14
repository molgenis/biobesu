#!/user/bin/env python3
import pytest

from biobesu.suite.vibe_versions.helper import converters

NON_EMPTY_STRING_ERR = 'list must contain non-empty strings'


def test_list_to_vibe_arguments_empty_list():
    input_list = []

    expected_output = ''
    actual_output = \
        converters.convert_list_to_arguments_with_same_key(input_list, '-m')

    assert actual_output == expected_output


def test_list_to_vibe_arguments_single_item():
    input_list = ['OMIM:012345']

    expected_output = '-m OMIM:012345'
    actual_output = \
        converters.convert_list_to_arguments_with_same_key(input_list, '-m')

    assert actual_output == expected_output


def test_list_to_vibe_arguments_list():
    input_list = ['OMIM:012345', 'OMIM:543210']

    expected_output = '-m OMIM:012345 -m OMIM:543210'
    actual_output = \
        converters.convert_list_to_arguments_with_same_key(input_list, '-m')

    assert actual_output == expected_output


def test_list_with_empty_strings_to_vibe_arguments_list():
    input_list = ['', '']

    with pytest.raises(ValueError) as err:
        converters.convert_list_to_arguments_with_same_key(input_list, '-m')

    assert str(err.value) == NON_EMPTY_STRING_ERR


def test_list_with_partly_empty_strings_to_vibe_arguments_list():
    input_list = ['OMIM:543210', '']

    with pytest.raises(ValueError) as err:
        converters.convert_list_to_arguments_with_same_key(input_list, '-m')

    assert str(err.value) == NON_EMPTY_STRING_ERR
