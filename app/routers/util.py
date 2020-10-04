import time
import secrets
from os import environ

from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2

import jwt

oauth2_scheme = OAuth2()


def enforce_authentication(token: str = Depends(oauth2_scheme)):
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'})

    try:
        payload = jwt.decode(token,
                             environ['JWT_SECRET'],
                             algorithms=['HS256'])

        if any(key not in payload for key in ('sub', 'iss')):
            raise invalid_credentials

        if payload['iss'] != 'boris-auth':
            raise invalid_credentials

        # `pyjwt` had already validated `exp` value.
    except jwt.PyJWTError:
        raise invalid_credentials

    return payload['sub']


def generate_message_id() -> str:
    prefix = str(time.time_ns())[2:]
    suffix = secrets.randbelow(2**16)
    return f'{prefix}{suffix}'
