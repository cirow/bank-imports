import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import io
    from adapters import PluxeeAdapter
    from core import rules


    return PluxeeAdapter, io, mo


@app.cell
def _(mo):
    file_area = mo.ui.file(kind="area")
    file_area
    return (file_area,)


@app.cell
def _(PluxeeAdapter, file_area, io):
    current_statement = PluxeeAdapter(io.BytesIO(file_area.contents())).to_statement()
    return


app._unparsable_cell(
    r"""

    mo.ui.table(data=pluxee_statement.df)mo.ui.table(data=current_statement.df)
    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
