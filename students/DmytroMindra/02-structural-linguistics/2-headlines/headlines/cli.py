import sys

import click

from headlines.app import ascii_cat, execute_evalset, execute_corpus


@click.command()
def cat():
    """Commits pending changes."""
    click.echo("cat")


@click.command()
@click.option('--cat/--no-cat', is_flag=True, default=True)
@click.option('--evalset', is_flag=True,  default=False)
@click.option('--corpus', is_flag=True,  default=False)
def run(cat, evalset, corpus):

    if cat:
        ascii_cat(sys.stdout)

    print('Homework 2-1: The Associated Press Stylebook')

    if evalset:
        execute_evalset()

    if corpus:
        execute_corpus()
