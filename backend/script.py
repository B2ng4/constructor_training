import os


def merge_files(directory, output_file, extensions, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = ['.venv']

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(directory):
            if any(exclude in root for exclude in exclude_dirs):
                continue
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            outfile.write(f'# Содержимое файла: {filepath}\n')
                            outfile.write(infile.read())
                            outfile.write('\n\n')
                    except Exception as e:
                        print(f'Не удалось прочитать файл {filepath}: {e}')


if __name__ == "__main__":
    directory_to_scan = r'/Users/timofeymac/PycharmProjects/events_knagu/backend'


    output_file_py = 'all_code.py'
    merge_files(
        directory=directory_to_scan,
        output_file=output_file_py,
        extensions=['.py']
    )
    print(f'Все .py файлы были собраны в {output_file_py}')

    output_file_data = 'all_data_files.txt'
    merge_files(
        directory=directory_to_scan,
        output_file=output_file_data,
        extensions=['.json', '.env', '.css']
    )
    print(f'Все .json и .env файлы были собраны в {output_file_data}')