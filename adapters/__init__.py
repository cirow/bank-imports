from adapters.base import StatementAdapter
from adapters.xp import XPAdapter
from adapters.mercadopago import MpagoAdapter
from adapters.nubank import NubankAdapter
from adapters.pluxee import PluxeeAdapter
from pathlib import Path
import csv
import io
import pdfplumber

__all__ = [
    "StatementAdapter",
    "XPAdapter",
    "MpagoAdapter",
    "NubankAdapter",
    "PluxeeAdapter",
    "detect",
]

_ADAPTERS = [XPAdapter, MpagoAdapter, NubankAdapter, PluxeeAdapter]


def detect(file, filename: str) -> type[StatementAdapter]:
    filetype = Path(filename).suffix.lower().lstrip(".")
    sig = _extract_signature(file, filetype)
    for adapter in _ADAPTERS:
        if adapter.matches(sig):
            return adapter
    raise ValueError(f"No adapter matched signature: '{sig}'")


def _extract_signature(file, filetype: str) -> str:
    if filetype == "pdf":
        with pdfplumber.open(file) as pdf:
            text = pdf.pages[0].extract_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return "_".join(lines[:2]).lower() + "_pdf"
    if filetype == "csv":
        if isinstance(file, (str, Path)):
            with open(file, newline="") as f:
                headers = next(csv.reader(f))
        else:
            content = file.read().decode("utf-8")
            file.seek(0)
            headers = next(csv.reader(io.StringIO(content)))
        return "_".join(sorted(h.lower() for h in headers)) + "_csv"

    raise ValueError(f"Unsupported file type: '{filetype}'")
