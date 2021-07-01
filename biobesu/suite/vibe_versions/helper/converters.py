#!/user/bin/env python3

from os import listdir


def list_to_vibe_arguments(argument_list, argument):
    # Checks whether any elements are given, and if so, whether the first one isn't an empty String.
    # In case multiple elements are given, it is assumed it's not a list containing empty Strings.
    if len(argument_list) > 0 and len(argument_list[0]) > 0:
        return f'{argument} ' + f' {argument} '.join(argument_list)
    else:
        return ''


def merge_vibe_simple_output_files(vibe_dir, out_file):
    with open(out_file, 'x') as file_writer:  # Requires creating a new file.
        # Write header.
        file_writer.write("id\tsuggested_genes\n")
        for vibe_out_file in listdir(vibe_dir):
            if not vibe_out_file.startswith('.'):  # Ignore hidden files such as .DS_Store.
                with open(vibe_dir + vibe_out_file) as file_reader:
                    file_name = vibe_out_file.split('.')[0]
                    genes = file_reader.readline()  # File should contain single comma separated line.
                    file_writer.write(f'{file_name}\t{genes}\n')
