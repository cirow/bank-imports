from core.statement import Statement
from adapters.base import StatementAdapter
import pandas as pd

class XPAdapter(StatementAdapter):
    columns = {"Data", "Estabelecimento", "Portador",	"Valor", "Parcela"}
    file_type = "csv"

    def __init__(self, filename):
        self.df = pd.read_csv(filename, sep=";", parse_dates=["Data"], date_format="%d/%m/%Y" )
        self.validate_columns(self.df)
        self.signature = self.generate_csv_adapter_signature()

    def to_statement(self):
        columns_remap={"Data": "date", "Estabelecimento": "place", "Valor": "amount", "Parcela": "installment"}
        columns_remove = ["Portador"]
        columns_add = ["category"]
        _df = self.df.copy()
        _df = _df.rename(columns=columns_remap)
        _df = _df.drop(columns_remove, axis=1)
        for c in columns_add:
            _df[c] = ""
        return Statement(_df)
