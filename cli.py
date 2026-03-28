import click
import filehandler

@click.group()
def cli():
    pass
@cli.command('classify')
@click.option('--filename', '-f', required=True, help='Filename')
@click.option("--type", "-t", required=True, help="Type of statement: xp, mercadopago")
def classify(filename, type):
    filehandler.classify(filename, type)

if __name__ == '__main__':
    cli()

