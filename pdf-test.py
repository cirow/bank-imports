import pdfplumber
import re
from datetime import date

meses = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12
}

def is_date(line):
    srch = re.search("^(segunda|terça|quarta|quinta|sexta)-feira|(sábado|domingo), (3[01]|[12][0-9]|[1-9]) (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", line)
    return srch != None

def is_amount(line):
    if "R$" in line:
        return True
    return False

def extract_date(line):
    day_month = line.split(",")[1].strip().split(" ")
    day = day_month[0]
    month = day_month[1]
    the_date = date(2026, meses[month], int(day))
    return the_date

def extract_amount(line):
    amount = float(line.split("R$")[1].strip().replace(",","."))
    return amount

pdf_text = ""
with pdfplumber.open("pluxee.pdf") as pdf:
    for page in pdf.pages:
        pdf_text += page.extract_text()
        pdf_text += "\n"

pdf_lines = pdf_text.splitlines()[4:]

i = 0
current_date = None
while (i < len(pdf_lines)):
    if(is_date(pdf_lines[i])):
        current_date = extract_date(pdf_lines[i])
        # print(current_date)
    else:
        if(pdf_lines[i] == "Compra no Alimentação"):
            amount = extract_amount(pdf_lines[i+1])
            description = pdf_lines[i+2]
            print(f"{current_date}: {description}: {amount}")
            i = i + 2

    i = i + 1

#
# while (i < len(pdf_lines)):
#     print(pdf_lines[i])
#     i = i + 1
