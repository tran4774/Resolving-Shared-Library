from os import listdir, path, system
from subprocess import check_output, DEVNULL
from argparse import ArgumentParser, BooleanOptionalAction
from sys import exit


def ls_files(directory, self_library):
    list_files = list()
    for item in listdir(directory):
        abspath = path.join(directory, item)
        try:
            if path.isdir(abspath):
                list_files = list_files + ls_files(abspath, self_library)
            else:
                list_files.append(abspath)
        except FileNotFoundError as err:
            print('invalid directory\n', 'Error: ', err)
    return list_files


def get_set_shared_object_library_one_file(file, self_library):
    set_files = set()
    try:
        output = check_output([f"ldd '{file}' | tr -s '[:blank:]' '\n' | grep '^/'"],
                              stderr=DEVNULL,
                              shell=True,
                              encoding='utf8')
        for library_name in output.split("\n"):
            if self_library:
                set_files.add(library_name)
            elif file.rpartition('/')[0] not in library_name:
                set_files.add(library_name)
    except Exception:
        pass
    set_files.discard('')
    return set_files


def get_set_shared_object_library(directory, self_library):
    files = ls_files(directory, self_library)
    set_files = set()
    for file in files:
        try:
            output = check_output([f"ldd '{file}' | tr -s '[:blank:]' '\n' | grep '^/'"],
                                  stderr=DEVNULL,
                                  shell=True,
                                  encoding='utf8')
            for library_name in output.split("\n"):
                if self_library:
                    set_files.add(library_name)
                elif directory not in library_name:
                    set_files.add(library_name)
        except Exception:
            pass
    set_files.discard('')
    return set_files


def main():
    parser = ArgumentParser(description="This executable file will help you resolve shared object library "
                                        "dependencies for building image with minimum number of files")
    parser.add_argument("-p", "--path", help="Path contain all files need to resolve shared object library")
    parser.add_argument("-f", "--file", help="File need to resolve shared object library")
    parser.add_argument("-d", "--destination", help="Destination folder to copy dependencies", default="deps")
    parser.add_argument("--self-library", help="Resolve self library or not",
                        action=BooleanOptionalAction,
                        default=False)
    args = parser.parse_args()

    set_dependencies = set()
    if args.path:
        set_dependencies = get_set_shared_object_library(args.path, args.self_library)
    elif args.file:
        set_dependencies = get_set_shared_object_library_one_file(args.file, args.self_library)
    else:
        print("No argument --file or --path are requested")
        exit(0)

    if len(set_dependencies) == 0:
        print("This file/folder has no dependency")
        exit(0)
    for i in set_dependencies:
        system(f"mkdir -p {args.destination}{i.rpartition('/')[0]}; cp {i} {args.destination}{i}")


main()
