import csv


def read_field_names(csv_path):
    with open(csv_path, newline="") as csv_handle:
        reader = csv.DictReader(csv_handle)
        return reader.fieldnames
