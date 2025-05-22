import logging

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from jose import jwt, JWTError
from jose.utils import base64url_decode
from jwt import ExpiredSignatureError

from .config import KEYCLOAK_JWKS_URL, KEYCLOAK_ISSUER, AUDIENCE, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID

# Keycloak authentication and JWT verification utilities for FastAPI.
auth_logger = logging.getLogger("app.auth")

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


def verify_token(token: str, requested_role: str = None) -> str:
    try:
        auth_logger.debug(f"Verifying token: {token}")

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
            auth_logger.error("Public key not found for the given token.")
            raise HTTPException(status_code=401, detail="Public key not found")

        # Step 3: Decode token
        auth_logger.debug(f"Public key found: {public_key}")
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=KEYCLOAK_ISSUER
        )
        # Step 4: Check roles if requested
        if requested_role:
            auth_logger.debug(f"Requested role: {requested_role}")
            roles = payload.get("resource_access", {}).get(KEYCLOAK_CLIENT_ID, {}).get("roles", [])
            if requested_role not in roles:
                auth_logger.error(f"User does not have the required role: {requested_role}")
                raise HTTPException(status_code=403, detail="Insufficient permissions")

        return payload.get("preferred_username", payload.get("sub"))

    except ExpiredSignatureError:
        auth_logger.info("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        auth_logger.error(f"JWT error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        # Print everything in the error, including the stack trace
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=401, detail=f"Unexpected error: {str(e)}")