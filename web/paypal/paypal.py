import hashlib


def create_ipn_hash(key):
    salt = '@k38!#$^'
    return hashlib.md5(''.join([
            salt,
            key,
            salt
        ])
    ).hexdigest()
