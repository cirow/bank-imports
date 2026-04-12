import click
from . import filehandler

@click.command()
@click.option('--filename', '-f', required=True, help='Filename')
@click.option("--type", "-t", required=True, help="Type of statement: xp, mercadopago")
@click.option("--month", "-m", default=0, help="Filter by month (1 - 12)")
@click.option("--year", "-y", default=0, help="Filter by year (default=current)")
def classify(filename, type, month, year):
    filehandler.classify(filename, type, month, year)

if __name__ == '__main__':
    classify()
