import csv
import statement

ASSIGNMENTS = []
_fieldnames = ['place', 'group_sales', 'category', 'rewrite_to']

def _assert_bool(value: str):
    return value.lower() == 'true'

def read(filename="categories.csv"):
    global ASSIGNMENTS
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, _fieldnames)
        for row in reader:
            if set(row.values()) == set(_fieldnames):
                continue
            row["group_sales"] = _assert_bool(row["group_sales"])
            ASSIGNMENTS.append(row)

def write(filename="categories.csv"):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, _fieldnames)
        writer.writeheader()
        for r in ASSIGNMENTS:
            writer.writerow(r)

def filter_date(s: statement.Statement, month: int, year: int) -> statement.Statement:
    if month or year:
        return statement.Statement(s.filter_date(month, year))
    return s

def apply(s: statement.Statement):
    for r in ASSIGNMENTS:
        if r["group_sales"]:
            s.group_similar_purchases(statement.Statement.PLACE_FIELD, r["place"])
        s.categorize_purchases(statement.Statement.PLACE_FIELD, r["place"], r["category"])
        if r["rewrite_to"] is not None:
            s.apply_place_rewrites(r["place"], r["rewrite_to"])
    return s

read()
