# MIT License
#
# Copyright (c) 2024 Mark Qvist / unsigned.io.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

KEY_PASSPHRASE = None
LOADED_KEY     = None

import os
import RNS
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from cryptography import __version__ as cryptography_version_str
try:
    cryptography_major_version = int(cryptography_version_str.split(".")[0])
except:
    RNS.log(f"Could not determine PyCA/cryptography version: {e}", RNS.LOG_ERROR)
    RNS.log(f"Assuming recent version with automatic backend selection", RNS.LOG_ERROR)

def get_key(key_path, force_reload=False):
    KEY_PATH = key_path
    key = None
    if LOADED_KEY != None and not force_reload:
        return LOADED_KEY
    elif os.path.isfile(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            if cryptography_major_version > 3:
                key = load_pem_private_key(f.read(), KEY_PASSPHRASE)
            else:
                from cryptography.hazmat.backends import default_backend
                key = load_pem_private_key(f.read(), KEY_PASSPHRASE, backend=default_backend())
    else:
        if cryptography_major_version > 3:
            key = ec.generate_private_key(curve=ec.SECP256R1())
        else:
            from cryptography.hazmat.backends import default_backend
            key = ec.generate_private_key(curve=ec.SECP256R1(), backend=default_backend())

        if KEY_PASSPHRASE == None:
            key_encryption = serialization.NoEncryption()
        else:
            key_encryption = serialization.BestAvailableEncryption(KEY_PASSPHRASE)

        with open(KEY_PATH, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=key_encryption))

    return key

def gen_cert(cert_path, key):
    CERT_PATH = cert_path
    cert_attrs = [x509.NameAttribute(NameOID.COUNTRY_NAME, "NA"),
                  x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "None"),
                  x509.NameAttribute(NameOID.LOCALITY_NAME, "Earth"),
                  x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sideband"),
                  x509.NameAttribute(NameOID.COMMON_NAME, "Sideband Repository")]

    issuer  = x509.Name(cert_attrs)
    subject = issuer

    cb = x509.CertificateBuilder()
    cb = cb.subject_name(subject)
    cb = cb.issuer_name(issuer)
    cb = cb.public_key(key.public_key())
    cb = cb.serial_number(x509.random_serial_number())
    cb = cb.not_valid_before(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=-14))
    cb = cb.not_valid_after(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=3652))
    cb = cb.add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)

    if cryptography_major_version > 3:
        cert = cb.sign(key, hashes.SHA256())
    else:
        from cryptography.hazmat.backends import default_backend
        cert = cb.sign(key, hashes.SHA256(), backend=default_backend())

    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

def ensure_certificate(key_path, cert_path):
    gen_cert(cert_path, get_key(key_path))
    return cert_path