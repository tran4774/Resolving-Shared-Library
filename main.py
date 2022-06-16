import os
import subprocess
import argparse


def ls_files(directory):
    list_files = list()
    for item in os.listdir(directory):
        abspath = os.path.join(directory, item)
        try:
            if os.path.isdir(abspath):
                list_files = list_files + ls_files(abspath)
            else:
                list_files.append(abspath)
        except FileNotFoundError as err:
            print('invalid directory\n', 'Error: ', err)
    return list_files


def get_set_shared_object_library_one_file(file):
    set_files = set()
    try:
        output = subprocess.check_output([f"ldd '{file}' | tr -s '[:blank:]' '\n' | grep '^/'"],
                                         stderr=subprocess.DEVNULL,
                                         shell=True,
                                         encoding='utf8')
        for library_name in output.split("\n"):
            set_files.add(library_name)
    except Exception:
        pass
    set_files.discard('')
    return set_files


def get_set_shared_object_library(path):
    files = ls_files(path)
    set_files = set()
    for file in files:
        set_files.update(get_set_shared_object_library_one_file(file))
    set_files.discard('')
    return set_files


def main():
    parser = argparse.ArgumentParser(description="Adding description")
    parser.add_argument("-p", "--path", help="Path contain all files need to resolve shared object library")
    parser.add_argument("-f", "--file", help="File need to resolve shared object library")
    parser.add_argument("-d", "--destination", help="Destination folder to copy dependencies")
    args = parser.parse_args()
    des = "deps"
    if args.destination:
        des = args.destination

    set_dependencies = set()
    if args.path:
        set_dependencies = get_set_shared_object_library(args.path)
    elif args.file:
        set_dependencies = get_set_shared_object_library_one_file(args.file)

    if len(set_dependencies) == 0:
        print("This file/folder has no dependency")
        exit(0)
    for i in set_dependencies:
        os.system(f"mkdir -p {des}{i.rpartition('/')[0]}; cp {i} {des}{i}")


main()