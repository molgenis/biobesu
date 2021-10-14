#!/user/bin/env python3

from biobesu.helper import readers


def test_two_columns_to_dict_stream_reader():
    input_string = ['id\tomim\n',
                    '0001\t012345,543210\n',
                    '0002\t456789,987654\n']

    expected_output = {'0001': '012345,543210', '0002': '456789,987654'}
    actual_output = readers.SeparatedValuesFileReader.key_value_stream_reader(input_string, 0, 1)

    assert actual_output == expected_output


def test_two_columns_to_dict_stream_reader_with_values_split():
    input_string = ['id\tomim\n',
                    '0001\t012345,543210\n',
                    '0002\t456789,987654\n']

    expected_output = {'0001': ['012345', '543210'], '0002': ['456789', '987654']}
    actual_output = readers.SeparatedValuesFileReader.key_value_stream_reader(input_string, 0, 1, values_separator=',')

    assert actual_output == expected_output
