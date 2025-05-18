# secureagent/config.py
import os

KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")

KEYCLOAK_ISSUER = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_AUTH_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/auth"
KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token"
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

AUDIENCE = "account"