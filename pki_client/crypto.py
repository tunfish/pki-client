# (c) 2018-2021 The Tunfish Developers
import os
from binascii import hexlify
from datetime import datetime
from pathlib import Path

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from hashids import Hashids


class AsymmetricKey:
    """
    Generate private key and submit a CSR.

    https://cryptography.io/en/latest/x509/tutorial.html#creating-a-certificate-signing-request-csr
    """

    KEY_SIZE = 4096

    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.csr = None
        self.cert = None

    def make_rsa_key(self):
        """
        Generate RSA key.
        """

        # Generate private key.
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.KEY_SIZE,
        )
        self.public_key = self.private_key.public_key()

    def make_csr(self, common_name_prefix: str = None):
        """
        Generate CSR.
        """

        # Create a random common name.
        common_name = Nagamani19().generate()
        if common_name_prefix:
            common_name = f"{common_name_prefix}-{common_name}"

        # Generate the CSR.
        csr_unsigned = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name(
                [
                    # Provide various details about who we are.
                    x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                ]
            )
        )

        # Sign the CSR with the private key.
        self.csr = csr_unsigned.sign(self.private_key, hashes.SHA512())

    def get_csr(self):
        """
        Return the CSR in PEM format.
        """
        return self.csr.public_bytes(serialization.Encoding.PEM)

    def submit_csr(self, url: str, profile: str):
        """
        Submit CSR to CA for autosigning.
        """
        csr_pem = self.get_csr()
        try:
            response = requests.post(
                url,
                data=csr_pem,
                params={"profile": profile},
                headers={"Content-Type": "application/x-pem-file"},
            )
            response.raise_for_status()
        except Exception as ex:
            raise ValueError(
                f"Automatically signing certificate failed: {ex}. Reason: {response.text}"
            )

        self.cert = x509.load_pem_x509_certificate(response.content)
        return self.cert.public_bytes(encoding=serialization.Encoding.PEM)

    def save_key(self, filename: Path):
        """
        Write the private key to disk for safe keeping.
        """
        with open(filename, "wb") as f:
            f.write(
                self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                    # encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
                )
            )

    def save_cert(self, filename: Path):
        """
        Write the certificate to disk.
        """
        with open(filename, "wb") as f:
            f.write(self.cert.public_bytes(encoding=serialization.Encoding.PEM))


class Nagamani:
    """
    Generate unique identifier.

    https://github.com/daq-tools/vasuki
    """

    precisions = {
        "s": 1,
        "ms": 1000,
        "ns": 1000000,
    }

    def nagamani_id(self, year, salt, precision):
        """
        Generate unique ids based on Hashids.
        Hashids are short, unique, non-sequential ids generated from numbers
        and suitable to be used as unguessable and unpredictable short UIDs.
        Here, we are generating Hashids of the current timestamp in milliseconds.
        To keep the footprint low, a custom epoch is used which starts on Jan 1, 2019.
        Examples::
            1Zk5zBoQ
            Y4Mvj5Zx
            2b4NBvYe
            XaMvl962
            yzgOlvap
        """

        assert type(year) is int, "Year must be integer"
        assert salt is not None, "Salt must be given"
        assert precision is not None, "Precision must be one of s, ms, ns"

        scaling = self.precisions.get(precision)

        duration = datetime.utcnow() - datetime(year, 1, 1)
        duration_scaled = int(duration.total_seconds() * scaling)
        return self.hashify(salt, duration_scaled)

    @staticmethod
    def hashify(salt, *data):
        """
        Hashids are short, unique, non-sequential ids generated from numbers
        and suitable to be used as short UIDs.
        If you want to decode the Hashids later, you should keep your salt stable.
        Remark: Hashids are not limited to encode a single number, you can actually
        pack a list of numbers into a single Hashid.
        - https://hashids.org/
        - https://hashids.org/python/
        - https://github.com/davidaurelio/hashids-python
        """
        hashids = Hashids(salt=salt)
        return hashids.encode(*data)


class Nagamani19(Nagamani):

    size_map = {"small": "s", "medium": "ms", "large": "ns"}

    def generate(self, size=None):
        salt = self.gensalt()
        precision = self.get_precision(size)
        return self.nagamani_id(2019, salt, precision)

    def get_precision(self, selector):
        selector = selector or "large"
        return self.size_map[selector]

    @staticmethod
    def gensalt():
        """
        This generates a salt from 24 random bytes from an OS-specific randomness source.
        The returned data should be unpredictable enough for cryptographic applications,
        though its exact quality depends on the OS implementation.
        https://docs.python.org/3/library/os.html#os.urandom
        Examples::
            b5f95cead701f2488d5668decb0d63a30e7ddb4c21f26574
            b4157e5459c88a6c454186492ee629ca097f8a60cbfb1a36
            de1ba437524e540e3b0d55617afcad5677b982d9e1f45f9d
        """
        return hexlify(os.urandom(24)).decode()


if __name__ == "__main__":
    akey = AsymmetricKey()
    akey.make_rsa_key()
    akey.make_csr()
    cert_pem = akey.submit_csr("http://localhost:8000/pki/RootCA/autosign")
    print(cert_pem.decode("utf-8"))
