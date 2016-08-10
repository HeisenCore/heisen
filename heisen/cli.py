#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

@click.command()
def main(args=None):
    """Console script for core"""
    click.echo("Replace this message by putting your code into "
                "core.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")


@click.group()
def cli():
    pass


@cli.command()
def run(args=None):
    from rpc.run import start_service
    start_service()


@cli.command()
def stop(args=None):
    from jsonrpclib import Server
    from socket import error
    from config.settings import RPC_PORT

    try:
        conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(RPC_PORT))
        conn.main.stop()

    except error:
        print 'Core Services shutdown \t\t\t\t\t\t[OK]'


if __name__ == "__main__":
    cli()
