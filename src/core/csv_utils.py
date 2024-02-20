import csv
import os
from itertools import islice
from typing import List


def csv_to_dict_generator(
    files_path: str,
    select_first_row: int = None,
    lower_header: bool = False,
):
    with open(files_path, encoding="utf-8-sig", newline="") as csv_file:
        if select_first_row:
            head = list(islice(csv_file, select_first_row))
        else:
            head = csv_file
        if lower_header:
            s = csv.reader(csv_file)
            fieldnames = [x.lower() for x in next(s, None)]
        else:
            fieldnames = None
        yield from csv.DictReader(head, delimiter=",", fieldnames=fieldnames)


def csv_to_list_dict(
    files_path: str, select_first_row: int = None
) -> List[csv.DictReader]:
    return list(csv_to_dict_generator(files_path, select_first_row))


def write_csv_file(file_path: str, csv_list: List[dict], fieldnames=None):
    """
    Write the extracted content into the file
    """
    if fieldnames is None:
        fieldnames = list(csv_list[0].keys())

    try:
        with open(file_path, "w+", encoding="utf-8-sig") as csv_file:
            write_to_csv_file(csv_file, fieldnames, csv_list)
    except FileNotFoundError:
        if not os.path.exists(file_path) and len(file_path.rsplit("/", maxsplit=1)) > 1:
            os.makedirs(file_path.rsplit("/", maxsplit=1)[0])
        print("Output file not present", file_path)
        print("Current dir: ", os.getcwd())
        with open(file_path, "w+", encoding="utf-8-sig") as csv_file:
            write_to_csv_file(csv_file, fieldnames, csv_list)


def write_to_csv_file(csv_file, fieldnames, csv_list):
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(csv_list)
