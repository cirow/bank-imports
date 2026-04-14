import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import io
    from adapters import XPAdapter, MpagoAdapter, NubankAdapter, PluxeeAdapter, detect
    from core import rules
    from core import categories
    from pathlib import Path


    return Path, detect, io, mo, rules


@app.cell(hide_code=True)
def _(mo):
    bank_colors = {
        "NubankAdapter": "#8A05BE",
        "XPAdapter": "#00A3E0",
        "MpagoAdapter": "#FF6600",
        "PluxeeAdapter": "#1B3C87",
    }


    def bank_badge(bank_name):
        if bank_name == "":
            return
        badge_color = bank_colors.get(bank_name, "#4CAF50")
        bank_label = bank_name.upper()
        return mo.Html(
            f'<span style="background-color: {badge_color}; color: white; padding: 4px 12px; '
            f'border-radius: 12px; font-size: 14px; font-weight: bold; display: inline-block;">'
            f'{bank_label}'
            f'</span>'
        )

    return (bank_badge,)


@app.cell
def _(mo):
    payee_name = mo.ui.dropdown(allow_select_none=True,options=["CIRO", "GUTA"])
    payee_name
    return (payee_name,)


@app.cell
def _(mo):
    file_area = mo.ui.file(kind="area")
    file_area
    return (file_area,)


@app.cell
def _(bank_badge, detect, file_area, io, mo, rules):
    mo.stop(file_area.contents() is None, mo.md("📎 Upload a file to get started"))

    file_area_contents = io.BytesIO(file_area.contents())
    adapter = detect(file_area_contents,file_area.name())
    current_statement = adapter(file_area_contents).to_statement()
    current_statement = rules.apply(current_statement)

    bank_badge(adapter.__name__.replace("Adapter", ""))
    return (current_statement,)


@app.cell
def _(payee_name):
    payee_name.value
    return


@app.cell
def _(current_statement, mo, payee_name):
    mo.ui.table(data=current_statement.to_sheets_df(payee=payee_name.value))
    return


@app.cell
def _(Path, mo):
    csv_path = Path("categories.csv")
    csv_editor = mo.ui.code_editor(value=csv_path.read_text())
    csv_editor
    return


if __name__ == "__main__":
    app.run()
