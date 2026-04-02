from statement import Statement
from pathlib import Path

class StatementAdapter:
    columns: set[str] = set()
    file_type: str = ""

    """Read file and validate the columns"""
    def __init__(self):
        pass

    """Convert the file to the Statement class standard"""
    def to_statement(self) -> Statement:
        raise NotImplementedError("Subclasses must implement to_statement()")

    def validate_file_type(self, filename: str):
        ext = Path(filename).suffix.lower().lstrip(".")
        if ext != self.file_type:
            raise ValueError(f"Invalid file type: expected '.{self.file_type}', got '.{ext}'")

    def validate_columns(self, df):
        missing = self.columns - set(df.columns)
        extra = set(df.columns) - self.columns
        if missing or extra:
            raise ValueError(f"Invalid columns:\nMissing: {missing}\nExtra: {extra}")
