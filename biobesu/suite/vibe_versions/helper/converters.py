#!/user/bin/env python3

from os import listdir


def convert_list_to_arguments_with_same_key(argument_list, argument_key):
    """
    Converts a list of items to command-line arguments. argument_list can be
    an empty list, though any strings in it should be non-empty.
    :param list[str] argument_list: the argument values
    :param str argument_key: the key to be used for the arguments
    :return: str
    :raise ValueError: if empty string is found in list
    """
    argument_string = ''

    for argument in argument_list:
        if len(argument) == 0:
            raise ValueError('list must contain non-empty strings')
        argument_string += f' {argument_key} {argument}'
    return argument_string.lstrip()


def merge_vibe_simple_output_files(vibe_dir, out_file):
    # Requires creating a new file.
    with open(out_file, 'x') as file_writer:
        # Write header.
        file_writer.write("id\tsuggested_genes\n")
        for vibe_out_file in listdir(vibe_dir):
            # Ignore hidden files such as .DS_Store.
            if not vibe_out_file.startswith('.'):
                with open(vibe_dir + vibe_out_file) as file_reader:
                    file_name = vibe_out_file.split('.')[0]
                    # File should contain single comma separated line.
                    genes = file_reader.readline()
                    file_writer.write(f'{file_name}\t{genes}\n')
