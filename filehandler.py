import click
import categories
from mercadopago_adapter import MpagoAdapter
import statement
from pathlib import Path
from xp_adapter import XPAdapter
from nubank_adapter import NubankAdapter

def classify(filename: str, type: str):
    the_statement = readFile(filename, type)
    the_statement = categorize(the_statement)
    writeStatement(filename, the_statement)

def readFile(filename, type) -> statement.Statement:
    click.echo("Reading file")
    match type:
        case "xp":
            return XPAdapter(filename).to_statement()
        case "mpago":
            return MpagoAdapter(filename).to_statement()
        case "nubank":
            return NubankAdapter(filename).to_statement()
        case _:
            click.echo("Error, unsupported statement type: {type}",err=True)
            exit(1)

def categorize(_statement: statement.Statement):
    for c in categories.CATEGORY_ASSIGMENT:
        if c["group_sales"]:
            _statement.group_similar_purchases(statement.Statement.PLACE_FIELD, c["place"])
        _statement.categorize_purchases(statement.Statement.PLACE_FIELD, c["place"], c["category"]) 
    click.echo(_statement)
    return _statement

def writeStatement(filename: str, _statement: statement.Statement):
    path = Path(filename)
    new_filename = path.with_name(f"{path.stem}_categorized.csv")
    _statement.df.to_csv(new_filename, sep=";", index=False)

