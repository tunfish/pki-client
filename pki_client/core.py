# (c) 2021 The Tunfish Developers
from pathlib import Path
from urllib.parse import urljoin

import requests

from pki_client.crypto import AsymmetricKey


class PkiClient:
    def __init__(self, ca_baseurl: str, ca_name: str):
        self.ca_baseurl = ca_baseurl
        self.ca_name = ca_name

    @property
    def cacert_url(self):
        return urljoin(self.ca_baseurl, f"/issuer/{self.ca_name}.pem")

    @property
    def autocert_url(self):
        return urljoin(self.ca_baseurl, f"/pki/{self.ca_name}/autosign")

    def save_cacert(self, ca_cert_path: Path):
        response = requests.get(self.cacert_url)
        response.raise_for_status()
        with open(ca_cert_path, "wb") as f:
            f.write(response.content)

    def mkcert(
        self,
        private_key_path: Path,
        cert_path: Path,
        profile: str,
        common_name_prefix: str = None,
    ):
        """
        Generate X.509 material and autosign it at CA.
        """

        akey = AsymmetricKey()
        akey.make_rsa_key()
        akey.make_csr(common_name_prefix=common_name_prefix)

        # Submit CSR to CA for auto-signing.
        akey.submit_csr(url=self.autocert_url, profile=profile)

        # Save key material to disk.
        akey.save_key(private_key_path)
        akey.save_cert(cert_path)
