from cryptography.x509 import CertificateSigningRequest

from pki_client.crypto import AsymmetricKey


def test_crypto():
    akey = AsymmetricKey()
    akey.make_rsa_key()
    akey.make_csr()

    assert isinstance(akey.csr, CertificateSigningRequest)
