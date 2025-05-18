import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from jose import jwt, JWTError
from jose.utils import base64url_decode
from jwt import ExpiredSignatureError

from .config import KEYCLOAK_JWKS_URL, KEYCLOAK_ISSUER, AUDIENCE, KEYCLOAK_REALM

# Keycloak authentication and JWT verification utilities for FastAPI.

# Cache the JWKS public keys
_jwks = None
def get_jwks():
    """
    Retrieve and cache the JSON Web Key Set (JWKS) from the Keycloak server.

    Returns:
        dict: The JWKS containing public keys for verifying JWTs.

    Raises:
        Exception: If the JWKS cannot be fetched from the Keycloak server.
    """

    global _jwks
    if _jwks is None:
        response = requests.get(KEYCLOAK_JWKS_URL)
        if response.status_code != 200:
            raise Exception("Failed to get JWKS")
        _jwks = response.json()
    return _jwks


def construct_rsa_public_key(jwk: dict):
    n_bytes = base64url_decode(jwk["n"].encode("utf-8"))
    e_bytes = base64url_decode(jwk["e"].encode("utf-8"))
    n = int.from_bytes(n_bytes, byteorder="big")
    e = int.from_bytes(e_bytes, byteorder="big")
    public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
    return public_key


def verify_token(token: str) -> str:
    try:
        # Step 1: Fetch JWKS
        jwks = requests.get(KEYCLOAK_JWKS_URL).json()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Step 2: Find matching key
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = construct_rsa_public_key(key)
                break

        if public_key is None:
            raise HTTPException(status_code=401, detail="Public key not found")

        # Step 3: Decode token
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=KEYCLOAK_ISSUER
        )

        return payload.get("preferred_username", payload.get("sub"))

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        # Print everythin in the error, including the stack trace
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=401, detail=f"Unexpected error: {str(e)}")