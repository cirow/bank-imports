import csv

CUSTOS_FIXOS = "Custos fixos"
PRAZERES = "Prazeres"
METAS = "Metas"
CONFORTO = "Conforto"
CONHECIMENTO = "Conhecimento"
LIBERDADE_FINANCEIRA = "Liberdade financeira"
CATEGORY_ASSIGMENT = []
category_table_fieldnames = ['place','group_sales','category', 'is_regex']

def assert_bool(value: str):
    return value.lower() == 'true'

def read_categories(filename = "categories.csv"):
    global CATEGORY_ASSIGMENT
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, category_table_fieldnames, restval='False')
        for row in reader:
            # Dicarding header line if it exists
            if set(row.values()) == set(category_table_fieldnames):
                continue
            # Asserting bool value
            row["is_regex"] = assert_bool(row["is_regex"])
            row["group_sales"] = assert_bool(row["group_sales"])
            CATEGORY_ASSIGMENT.append(row)
            print(row)

def write_categories(filename = "categories.csv"):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["place", "group_sales", "category"]
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        for c in CATEGORY_ASSIGMENT:
            writer.writerow(CATEGORY_ASSIGMENT[c])

read_categories()

