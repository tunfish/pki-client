# (c) 2021 The Tunfish Developers
from pathlib import Path
from urllib.parse import urlparse

import click
import validators

from pki_client.core import PkiClient


@click.command(help="""Convenient PKI client""")
@click.option(
    "--ca-url",
    type=click.STRING,
    help="The system base URL of the CA",
    required=True,
)
@click.option(
    "--ca-name",
    type=click.STRING,
    help="The name of the CA",
    required=True,
)
@click.option(
    "--cacert",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
    help="Path where to save the CA certificate",
    required=True,
)
@click.option(
    "--key",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
    help="Path where to save the private key",
    required=True,
)
@click.option(
    "--certificate",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
    help="Path where to save the certificate",
    required=True,
)
@click.option(
    "--common-name-prefix",
    type=click.STRING,
    help="Prefix for the common name (CN)",
    required=False,
)
@click.option(
    "--profile",
    type=click.STRING,
    help="Profile for certificate purpose (server, webserver, client, enduser, ocsp)",
    required=True,
)
def main(
    ca_url: str,
    ca_name: str,
    cacert: Path,
    key: Path,
    certificate: Path,
    common_name_prefix: str,
    profile: str,
):
    #checked_url = validators.url(ca_url)
    #if not checked_url:
    #    raise ValueError(f"ERROR: Invalid URL '{ca_url}'")
    client = PkiClient(ca_baseurl=ca_url, ca_name=ca_name)
    client.save_cacert(cacert)
    client.mkcert(
        private_key_path=key,
        cert_path=certificate,
        profile=profile,
        common_name_prefix=common_name_prefix,
    )
