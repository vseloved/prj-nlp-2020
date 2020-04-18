import sys

import click

from headlines.app import ascii_cat, execute_evalset, execute_corpus, execute_virality


@click.command()
def cat():
    """Commits pending changes."""
    click.echo("cat")


@click.command()
@click.option('--cat/--no-cat', is_flag=True, default=True)
@click.option('--evalset', is_flag=True,  default=False)
@click.option('--corpus', is_flag=True,  default=False)
@click.option('--virality', is_flag=True,  default=False)
def run(cat, evalset, corpus, virality):

    if cat:
        ascii_cat(sys.stdout)

    if evalset:
        print('Homework 2-1: The Associated Press Stylebook')
        execute_evalset()

    if corpus:
        print('Homework 2-1: The Associated Press Stylebook')
        execute_corpus()

    if virality:
        print('Homework 2-2: Headline Virality')
        execute_virality()