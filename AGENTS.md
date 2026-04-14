## What This Project Is

Home finance tool for processing Brazilian bank statements. It parses CSV/PDF exports from banks, applies categorization rules, and outputs structured data. The end goal is to feed a Google Sheets ledger shared with a non-technical partner, via an n8n webhook.

Two interfaces exist: a CLI for the developer and a Marimo web app for interactive review. Both share the same core pipeline.

---

## Architecture

```
file input (path or BytesIO)
    ↓
detect(file, filename)              adapters/__init__.py
    ↓
AdapterClass(file).to_statement()   adapters/{bank}.py
    ↓
Statement(df)                       core/statement.py
    ↓
rules.filter_date(s, month, year)   core/rules.py
rules.apply(s)
    ↓
output (CSV write / table display / n8n webhook)
```

**Three layers — never cross them sideways:**

- `adapters/` — format-specific parsers. One file per bank. All converge on `Statement`.
- `core/` — domain model (`Statement`), rule engine (`rules.py`), category enum (`categories.py`).
- `interfaces/` — UI layers. `cli/` and `marimo/` are peers. They import from `core/` and `adapters/` only. Never from each other.

---

## Module Map

| Module | Purpose |
|--------|---------|
| `core/statement.py` | `Statement` class. The canonical data model. Every adapter produces one of these. |
| `core/rules.py` | Reads `categories.csv`. Exposes `apply(statement)` and `filter_date(statement, month, year)`. |
| `core/categories.py` | `Category` StrEnum. Same read/write/apply API as rules.py. |
| `adapters/base.py` | `StatementAdapter` ABC. Signature generation and matching logic. |
| `adapters/__init__.py` | `detect(file, filename)` factory. Holds `_ADAPTERS` registry list. |
| `adapters/nubank.py` | Nubank CSV. Columns: date, title, amount. Separator: `,`. |
| `adapters/xp.py` | XP CSV. Columns: Data, Estabelecimento, Portador, Valor, Parcela. Separator: `;`. |
| `adapters/mercadopago.py` | Mercado Pago CSV. Header on row 3 (`header=2`). Separator: `;`. |
| `adapters/pluxee.py` | Pluxee PDF. State-machine parser. Portuguese month names. |
| `interfaces/cli/main.py` | Click entrypoint only. No logic. |
| `interfaces/cli/filehandler.py` | CLI orchestration: read → filter → apply → write CSV. |
| `interfaces/marimo/__init__.py` | `run()` and `edit()` subprocess wrappers. |
| `interfaces/marimo/statement_importer.py` | Marimo notebook. Upload → detect → preview table. |

---

## Running the Project

```bash
# CLI
uv run classify -f file.csv                          # auto-detect bank
uv run classify -f file.csv -t nubank               # explicit type
uv run classify -f file.csv -m 3                    # filter march, current year
uv run classify -f file.csv -m 3 -y 2026            # filter march 2026

# Marimo
uv run marimo-edit                                   # open notebook in editor
uv run marimo-run                                    # run notebook as app
```

Valid `--type` values: `xp`, `mpago`, `nubank`, `pluxee`

After classify runs, output is written to `{stem}_categorized.csv` in the same directory as the input file.

---

## The Statement Contract

`Statement` is the single handoff point between adapters and the rule engine. It validates strictly on construction — extra or missing columns raise `ValueError`.

**Required columns (exactly these five):**

| Column | Pandas dtype | Notes |
|--------|-------------|-------|
| `date` | datetime64[ns] | Adapter must parse before passing to Statement |
| `place` | string | **Must be uppercase.** This is what rules match against. |
| `amount` | Decimal | Never float. Statement applies `brl_to_decimal` on init. |
| `installment` | string | Empty string `""` if not applicable. |
| `category` | string | Empty string `""` until `rules.apply()` runs. |

**Key methods:**

- `filter_date(month, year)` — returns a filtered DataFrame (not a Statement — known inconsistency, callers wrap in `Statement()`)
- `to_sheets_df(payee="PAYEE_NAME")` — returns a formatted DataFrame for Sheets export: date as `DD/MM/YYYY`, amount as `"72,23"` (comma decimal), payee placeholder column added
- `group_similar_purchases(label, label_text)` — aggregates rows matching substring into first row
- `categorize_purchases(label, label_text, category)` — sets category on matching rows
- `apply_place_rewrites(old_place, new_place)` — exact string replace on place field

---

## Adding a New Bank Adapter

### 1. Create `adapters/newbank.py`

```python
from core.statement import Statement
from adapters.base import StatementAdapter
import pandas as pd

class NewBankAdapter(StatementAdapter):
    columns = {"RawCol1", "RawCol2", "RawCol3"}  # exact source column names
    file_type = "csv"  # or "pdf"

    def __init__(self, filename):
        self.df = pd.read_csv(filename, sep=",")
        self.validate_columns(self.df)
        self.signature = self.generate_csv_adapter_signature()

    def to_statement(self) -> Statement:
        _df = self.df.copy()
        _df = _df.rename(columns={"RawCol1": "date", "RawCol2": "place", "RawCol3": "amount"})
        _df["place"] = _df["place"].str.upper()   # mandatory
        _df["installment"] = ""                    # mandatory if not in source
        _df["category"] = ""                       # mandatory
        return Statement(_df)
```

For a **PDF adapter**, hardcode signature and override `matches()`:

```python
class NewPdfAdapter(StatementAdapter):
    file_type = "pdf"
    signature = "firstline_secondline_pdf"  # lowercase, from actual PDF text

    @classmethod
    def matches(cls, file_signature: str) -> bool:
        return cls.signature == file_signature
```

### 2. Register in `adapters/__init__.py`

```python
from adapters.newbank import NewBankAdapter          # add import

__all__ = [..., "NewBankAdapter"]                    # add to exports

_ADAPTERS = [XPAdapter, MpagoAdapter, NubankAdapter, PluxeeAdapter, NewBankAdapter]  # add to list
```

Order in `_ADAPTERS` matters — first match wins. Put more specific adapters before general ones.

### 3. Add to the explicit type match in `interfaces/cli/filehandler.py`

```python
case "newbank":
    return NewBankAdapter(filename).to_statement()
```

### Adapter checklist

- [ ] Place field uppercased with `.str.upper()` before `Statement()`
- [ ] `installment` and `category` added as empty strings if not in source
- [ ] `validate_columns(self.df)` called after loading
- [ ] `self.signature` set at end of `__init__`
- [ ] No `validate_file_type()` call (removed — detection already confirmed type)

---

## Signature-Based Detection

File type is determined from the filename extension (not file contents). The signature encodes what's inside.

**CSV signature** — auto-computed from `cls.columns`:
```
sorted(column_names, lowercased), joined with "_", appended with "_csv"
```
Example: `{"date", "title", "amount"}` → `"amount_date_title_csv"`

**PDF signature** — hardcoded class attribute:
```
first two non-empty lines of page 1, lowercased, joined with "_", appended with "_pdf"
```
Example: `"extrato_multibenefícios_pdf"`

`detect(file, filename)` accepts:
- `file`: `str` path **or** `io.BytesIO` (for Marimo uploads — BytesIO is seeked back to 0 after signature extraction)
- `filename`: always a `str` — used solely for extension detection

To debug a detection failure, run `_extract_signature(file, filetype)` directly to see what signature the file produces, then compare against adapter signatures.

---

## Rules Engine

Rules live in `categories.csv`. This file is **loaded once at module import** of `core/rules.py`. Changing the file requires a process restart.

**CSV columns:** `place, group_sales, category, rewrite_to`

| Field | Type | Behavior |
|-------|------|---------|
| `place` | string | Substring matched against transaction place via `str.contains()`. **Must be uppercase** to match adapter output. |
| `group_sales` | `"true"`/`"false"` | Aggregate all matching transactions into one row (sum amounts) |
| `category` | Category enum value | Set on matching rows |
| `rewrite_to` | string or empty | Rename place field after categorization. Empty = no rename. |

Rules are applied in order. Per rule: `group_similar_purchases` → `categorize_purchases` → `apply_place_rewrites`.

**Adding a rule**: edit `categories.csv` directly. No code changes needed.

---

## Conventions

### DataFrame mutations — always copy first

```python
# correct
_df = self.df.copy()
_df.loc[condition] = value
self.df = _df

# wrong — mutates in place
self.df.loc[condition] = value
```

### Amounts — always Decimal, never float

```python
from decimal import Decimal
amount = Decimal("72.23")   # correct
amount = 72.23              # wrong — floating point precision errors in financial data
```

`Statement.brl_to_decimal()` handles parsing from BRL string format (`"R$ 1.234,56"`).

### Place matching is case-sensitive

Adapters uppercase place. Rules must also be uppercase. Lowercase rules will silently never match.

### Errors — raise, don't swallow

Raise `ValueError` with a clear message. The exception to this is `PluxeeAdapter`, which collects parse errors in `self.errors` (list) because the PDF format is noisy. Always surface `self.errors` in the UI when using Pluxee.

### No logic in interface files

`interfaces/cli/main.py` and `interfaces/marimo/__init__.py` are thin wrappers. Business logic belongs in `core/` or `adapters/`.

---

## Known Issues

Do not work around these — fix at source when addressed.

| Location | Issue |
|----------|-------|
| `adapters/pluxee.py:64` | Year hardcoded to `2026` in `date(2026, ...)`. Will fail for 2027+ transactions. Fix: extract year from PDF header or use `datetime.now().year`. |
| `core/statement.py` `filter_date()` | Returns a raw `DataFrame`, not a `Statement`. Callers must wrap in `Statement()` manually. Inconsistent with the rest of the API. |
| `adapters/mercadopago.py` | Place field not uppercased in `to_statement()`. Rules won't match Mpago transactions unless the rule is lowercased (it shouldn't be). |
| `pyproject.toml` | `pydantic-ai` declared but not yet wired up. Intended for AI assistance within the Marimo interface. |
| `file-sig.py` (root) | Dead code. Safe to delete. |

---

## Domain Knowledge

### Brazilian currency (BRL)
- Thousand separator: `.` (dot)
- Decimal separator: `,` (comma)
- Examples: `R$ 1.234,56`, `72,23`
- `Statement.brl_to_decimal()` handles all BRL string formats

### Date formats by source

| Bank | Raw format | Example |
|------|-----------|---------|
| Nubank | ISO `YYYY-MM-DD` | `2026-03-28` |
| XP | Brazilian `DD/MM/YYYY` | `28/03/2026` |
| Mercado Pago | varies | adapter handles |
| Pluxee PDF | Portuguese weekday + day + month | `segunda-feira, 28 março` |
| Sheets export | Brazilian `DD/MM/YYYY` | `28/03/2026` |

### Pluxee
Pluxee (formerly Sodexo) is a Brazilian meal/food voucher card. The PDF export contains only food purchases labeled `"Compra no Alimentação"`. Other line types (`"Saldo liberado"`, `"Agendamento de Benefício"`) are skipped. The state machine in `_parse_transactions()` is sensitive to PDF layout changes.

---

## Planned Features — Don't Break These Paths

These are not yet implemented but the architecture must accommodate them:

- **n8n webhook + Google Sheets**: `to_sheets_df()` output will be POSTed to an n8n webhook that appends rows to a shared Google Sheet. n8n is the single owner of Sheets I/O.
- **Idempotent commits**: transactions will be hashed (`bank + amount + date`) before sending. Existing hashes fetched from Sheets on Marimo load; only new rows sent on commit.
- **Marimo commit flow**: Render button → preview table → tweak rules → Commit button (fires webhook). The commit cell does not exist yet.
- **Rules as a class**: `core/rules.py` global `ASSIGNMENTS` state will be replaced with a class instance. Don't add new callers that depend on the global.
- **AI assistance in Marimo**: `pydantic-ai` is wired into the Marimo interface — not a standalone categorizer, but AI features surfaced directly in the web UI.
- **Additional input sources**: Telegram messages, PWA receipts — all will feed the same Sheets backend.
