#!/user/bin/env python3

class SeparatedValuesFileReader:
    DEFAULT_SEPARATOR = '\t'
    DEFAULT_VALUES_SEPARATOR = None
    DEFAULT_SKIP_FIRST_LINE = True

    @staticmethod
    def key_value_reader(input_file, key_column, value_column,
                         separator=DEFAULT_SEPARATOR,
                         values_separator=DEFAULT_VALUES_SEPARATOR,
                         skip_first_line=DEFAULT_SKIP_FIRST_LINE):
        """
        Wrapper for :func:`SeparatedValuesFileReader.two_columns_to_dict_stream_reader`.

        :param input_file: path to the input file
        :type input_file: str
        :param key_column: the column which should be used as dict key
        :type key_column: int
        :param value_column: the column which should be used as dict value(s)
        :type value_column: int
        :param separator: the separator between the columns
        :type separator: str
        :param values_separator: the separator between individual values of the value column (if any)
        :type values_separator: None | str
        :param skip_first_line: wether the first line should be skipped (header line present)
        :type skip_first_line: bool
        :return: a dictionary with the digested data
        :rtype: dict[str,str] | dict[str,list[str]]
        """
        with open(input_file) as stream:
            return SeparatedValuesFileReader.key_value_stream_reader(stream, key_column, value_column,
                                                                     separator, values_separator,
                                                                     skip_first_line)

    @staticmethod
    def key_value_stream_reader(stream, key_column, value_column,
                                separator=DEFAULT_SEPARATOR,
                                values_separator=DEFAULT_VALUES_SEPARATOR,
                                skip_first_line=DEFAULT_SKIP_FIRST_LINE):
        """
        Reads a stream and retrieves 2 columns, which are converted into a dict
        (optionally with the values being split into a list).

        :param stream: the opened file (or list of strings representing the file)
        :type stream: TextIO | list[str]
        :param key_column: the column which should be used as dict key
        :type key_column: int
        :param value_column: the column which should be used as dict value(s)
        :type value_column: int
        :param separator: the separator between the columns
        :type separator: str
        :param values_separator: the separator between individual values of the value column (if any)
        :type values_separator: None | str
        :param skip_first_line: wether the first line should be skipped (header line present)
        :type skip_first_line: bool
        :return: a dictionary with the digested data
        :rtype: dict[str,str] | dict[str,list[str]]
        """
        # Dict to store data in.
        data_dict = {}

        # Processes file.
        for i, line in enumerate(stream):
            # Skip header line.
            if skip_first_line and i == 0:
                continue

            # Splits columns.
            line_splits = line.split(separator)

            # Only splits values if defined values_separator != None.
            if values_separator is None:
                data_dict[line_splits[key_column].strip()] = line_splits[value_column].strip()
            else:
                data_dict[line_splits[key_column].strip()] = line_splits[value_column].strip().split(values_separator)

        return data_dict
