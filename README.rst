##########
PKI client
##########


About
=====

A convenient client to interact with `tunfish-ca`_, a slightly improved
`django-ca`_. Its purpose is to easily create a RSA private/public key
pair and then have the CA create a certificate.


Synopsis
========

::

    pki-client \
        --ca-url=http://127.0.0.1:8000/ --ca-name=RootCA \
        --cacert=cacert.pem --key=example.key --certificate=example.pem --profile=server --common-name-prefix=node


.. _tunfish-ca: https://github.com/tunfish/tunfish-ca
.. _django-ca: https://github.com/mathiasertl/django-ca
