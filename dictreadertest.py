import csv


fieldnames = ['place','group_sales','category', 'is_regex']
with open("categories-regex.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames, restval='False')
    for l in reader:
        l['is_regex'] = l['is_regex'].lower() == "true"
        print(f"{l}")
