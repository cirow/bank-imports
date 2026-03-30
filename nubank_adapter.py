from statement import Statement
from statement_adapter import StatementAdapter
import pandas as pd

class NubankAdapter(StatementAdapter):
    columns = {"date", "title",	"amount"}

    def __init__(self, filename):
        self.df = pd.read_csv(filename, sep=",", parse_dates=["date"], date_format="%Y-%m-%d" )
        self.validate_columns(self.df)

    def to_statement(self):
        columns_remap={"title": "place"}
        columns_add = ["category", "installment"]
        _df = self.df.copy()
        _df = _df.rename(columns=columns_remap)
        _df["place"] = _df["place"].str.upper()

        for c in columns_add:
            _df[c] = ""
        return Statement(_df)

