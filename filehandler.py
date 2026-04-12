import click
import rules
import statement
from pathlib import Path
from adapters import XPAdapter, MpagoAdapter, NubankAdapter, PluxeeAdapter

def classify(filename: str, type: str, month: int, year: int):
    the_statement = readFile(filename, type)
    the_statement = rules.filter_date(the_statement, month, year)
    the_statement = rules.apply(the_statement)
    click.echo(the_statement)
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
        case "pluxee":
            return PluxeeAdapter(filename).to_statement()
        case _:
            click.echo("Error, unsupported statement type: {type}",err=True)
            exit(1)

def writeStatement(filename: str, _statement: statement.Statement):
    path = Path(filename)
    new_filename = path.with_name(f"{path.stem}_categorized.csv")
    _statement.df.to_csv(new_filename, sep=";", index=False)

