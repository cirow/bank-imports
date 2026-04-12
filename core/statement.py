import pandas as pd
import calendar
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

class Statement:
    DATE_FIELD = "date"
    PLACE_FIELD = "place"
    AMOUNT_FIELD = "amount"
    INSTALLMENT_FIELD = "installment"
    CATEGORY_FIELD = "category"
    columns = {DATE_FIELD, PLACE_FIELD, AMOUNT_FIELD, INSTALLMENT_FIELD, CATEGORY_FIELD}

    def __str__(self):
        return self.df.__str__()

    def __init__(self, df: pd.DataFrame):
        # Verifying columns standarizations
        missing = Statement.columns - set(df.columns)
        extra = set(df.columns) - Statement.columns
        if missing or extra:
            raise ValueError(f"Invalid columns for Statement:\nMissing: {missing}\nExtra: {extra}")
        self.df = df.copy()
        # Aplying the correct dtypes
        self.df[Statement.DATE_FIELD] = df[Statement.DATE_FIELD].astype('datetime64[ns]')
        self.df[Statement.PLACE_FIELD] = df[Statement.PLACE_FIELD].astype('string')
        self.df[Statement.INSTALLMENT_FIELD] = df[Statement.INSTALLMENT_FIELD].astype('string')
        self.df[Statement.CATEGORY_FIELD] = df[Statement.CATEGORY_FIELD].astype('string')

        # Changing amount field to decimal
        self.df[Statement.AMOUNT_FIELD] = self.df[Statement.AMOUNT_FIELD].apply(Statement.brl_to_decimal)

    @staticmethod
    def brl_to_decimal(brl) -> Decimal:
        if not brl:
            return Decimal('0')
        _dec = None
        if isinstance(brl, Decimal):
            return brl 
        if isinstance(brl, str):
            _dec = Decimal(brl.replace("R$","").replace(" ","").replace(".","").replace(",","."))
        elif isinstance(brl, float):
            _dec = Decimal(brl)
        return _dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def rewrite_place(self, place_old, place_new):
        _new_df = self.df.copy()
        _new_df.loc[_new_df[Statement.PLACE_FIELD].str.contains(place_old), Statement.PLACE_FIELD] = place_new 
        self.df = _new_df

    def group_similar_purchases(self, label: str, label_text: str):
        _aggregate = self.df.loc[self.df[label].str.contains(label_text)].copy()
        if len(_aggregate.index) <= 0:
            return
        _aggregate.iloc[0, _aggregate.columns.get_loc(Statement.AMOUNT_FIELD)] = _aggregate[Statement.AMOUNT_FIELD].sum()
        _new_df = self.df.copy()
        _new_df.loc[_aggregate.iloc[0].name] = _aggregate.iloc[0]
        _new_df = _new_df.loc[~_new_df.index.isin(_aggregate.index[1:])].copy()
        self.df = _new_df

    def apply_place_rewrites(self, old_place, new_place):
        _df = self.df.copy()
        _df.loc[_df[Statement.PLACE_FIELD] == old_place, Statement.PLACE_FIELD] = new_place 
        self.df = _df
        
    def categorize_purchases(self, label: str, label_text: str, category: str):
        _df = self.df.copy()
        _df.loc[_df[label].str.contains(label_text), Statement.CATEGORY_FIELD] = category
        self.df = _df

    def filter_date(self, month, year):
        if year == 0:
            year = datetime.now().year
        if month == 0:
            from_date = pd.to_datetime(f"{year:04d}-01-01")
            to_date = pd.to_datetime(f"{year:04d}-12-31")
        else:
            last_day = calendar.monthrange(2026, month)[1]
            from_date = pd.to_datetime(f"2026-{month:02d}-01")
            to_date = pd.to_datetime(f"2026-{month:02d}-{last_day:02d}")

        return(self.df[self.df[self.DATE_FIELD].between(from_date, to_date)])
