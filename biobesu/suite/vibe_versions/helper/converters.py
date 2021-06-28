#!/user/bin/env python3

from os import listdir


def list_to_vibe_arguments(argument_list, argument):
    if len(argument_list) > 0:
        return f'{argument} ' + f' {argument} '.join(argument_list)
    else:
        return ''


def merge_vibe_simple_output_files(vibe_dir, out_file):
    with open(out_file, 'x') as file_writer:  # Requires creating a new file.
        # Write header.
        file_writer.write("id\tgene_ids\n")
        for vibe_out_file in listdir(vibe_dir):
            with open(vibe_dir + vibe_out_file) as file_reader:
                file_name = vibe_out_file.split('.')[0]
                genes = file_reader.readline()  # File should contain single comma separated line.
                file_writer.write(f'{file_name}\t{genes}\n')
