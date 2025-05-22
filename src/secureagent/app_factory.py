# src/secureagent/app_factory.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2AuthorizationCodeBearer

from .config import KEYCLOAK_AUTH_URL, KEYCLOAK_TOKEN_URL, KEYCLOAK_BASE_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=KEYCLOAK_AUTH_URL,
    tokenUrl=KEYCLOAK_TOKEN_URL,
)

def create_app(
        title: str,
        description: str,
        version: str,
        origins: list,
):
    _app = FastAPI(
        title=title,
        description=description,
        version=version,
        swagger_ui_init_oauth={
            "clientId": f"{KEYCLOAK_CLIENT_ID}",
            "usePkceWithAuthorizationCodeGrant": True
        }
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def custom_openapi():
        if _app.openapi_schema:
            return _app.openapi_schema
        openapi_schema = get_openapi(
            title=title,
            version=version,
            description=description,
            routes=_app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2AuthorizationCodeBearer": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth",
                        "tokenUrl": f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
                        "scopes": {}
                    }
                }
            }
        }
        openapi_schema["security"] = [{"OAuth2AuthorizationCodeBearer": []}]
        _app.openapi_schema = openapi_schema
        return _app.openapi_schema

    _app.openapi = custom_openapi
    return _app
