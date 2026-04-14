from core.statement import Statement
from adapters.base import StatementAdapter
import pandas as pd
import pdfplumber
import re
from datetime import date, datetime

MESES = {
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

HEADER_LINES = 4
IGNORED_LINES = {"Saldo liberado", "Agendamento de Benefício"}


class PluxeeAdapter(StatementAdapter):
    columns = {"date", "amount", "place"}
    file_type = "pdf"
    signature = "extrato_multibenefícios_pdf"

    @classmethod
    def matches(cls, file_signature: str) -> bool:
        return cls.signature == file_signature

    def __init__(self, filename):
        pdf_text = self._extract_pdf_text(filename)
        self.df, self.errors = self._parse_transactions(pdf_text)
        self.validate_columns(self.df)

    def to_statement(self):
        columns_add = ["category", "installment"]
        _df = self.df.copy()
        _df["place"] = _df["place"].str.upper()

        for c in columns_add:
            _df[c] = ""
        return Statement(_df)

    @staticmethod
    def _is_date(line):
        srch = re.search("^(segunda|terça|quarta|quinta|sexta)-feira|(sábado|domingo), (3[01]|[12][0-9]|[1-9]) (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", line)
        return srch is not None

    @staticmethod
    def _is_amount(line):
        return "R$" in line

    @staticmethod
    def _extract_date(line, year):
        day_month = line.split(",")[1].strip().split(" ")
        day = day_month[0]
        month = day_month[1]
        return date(year, MESES[month], int(day))

    @staticmethod
    def _extract_amount(line):
        return float(line.split("R$")[1].strip().replace(",", "."))

    @staticmethod
    def _extract_pdf_text(filename):
        pdf_text = ""
        with pdfplumber.open(filename) as pdf:
            for page in pdf.pages:
                pdf_text += page.extract_text()
                pdf_text += "\n"
        return pdf_text

    def _parse_transactions(self, pdf_text):
        pdf_lines = pdf_text.splitlines()[HEADER_LINES:]

        i = 0
        current_date = None
        current_year = datetime.now().year
        last_month = None
        transactions = []
        errors = []

        while i < len(pdf_lines):
            line = pdf_lines[i]

            if self._is_date(line):
                month_str = line.split(",")[1].strip().split(" ")[1]
                month = MESES[month_str]
                if last_month is not None and month > last_month:
                    current_year -= 1
                last_month = month
                current_date = self._extract_date(line, current_year)
            elif line == "Compra no Alimentação":
                if not self._is_amount(pdf_lines[i + 1]):
                    errors.append(f"'Compra no Alimentação' not followed by valid amount. Got: {pdf_lines[i + 1]}")
                    i += 1
                    continue
                amount = self._extract_amount(pdf_lines[i + 1])
                place = pdf_lines[i + 2]
                transactions.append((current_date, amount, place))
                i += 2
            elif line in IGNORED_LINES:
                i += 2  # skip amount + description lines
            else:
                errors.append(f"Unrecognized line: {line}")

            i += 1

        df = pd.DataFrame(transactions, columns=["date", "amount", "place"])
        return df, errors
