from statement import Statement
from adapters.base import StatementAdapter
import pandas as pd

class MpagoAdapter(StatementAdapter):
    columns = {"RELEASE_DATE", "TRANSACTION_TYPE", "REFERENCE_ID",	"TRANSACTION_NET_AMOUNT", "PARTIAL_BALANCE"}
    file_type = "csv"

    def __init__(self, filename):
        self.validate_file_type(filename)
        self.df = pd.read_csv(filename, header=2, sep=";")
        self.validate_columns(self.df)

    def to_statement(self) -> Statement:
        columns_remap={"RELEASE_DATE": "date", "TRANSACTION_TYPE": "place", "TRANSACTION_NET_AMOUNT": "amount"}
        columns_remove = ["PARTIAL_BALANCE", "REFERENCE_ID"]
        columns_add = ["installment", "category"]
        _df = self.df.copy()
        _df = _df.rename(columns=columns_remap)
        _df = _df.drop(columns_remove, axis=1)
        for c in columns_add:
            _df[c] = ""
        return Statement(_df)
