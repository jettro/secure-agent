import os

from dotenv import load_dotenv
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings

from .session import get_user_session

load_dotenv()

from .auth import verify_token
from .config import KEYCLOAK_AUTH_URL, KEYCLOAK_TOKEN_URL, KEYCLOAK_BASE_URL, KEYCLOAK_REALM

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=KEYCLOAK_AUTH_URL,
    tokenUrl=KEYCLOAK_TOKEN_URL,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="HR Agent API",
        version="1.0",
        description="Agent with Keycloak-based security and Swagger OAuth2 login.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2": {
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

    # Apply OAuth2 globally to all endpoints if desired
    openapi_schema["security"] = [{"OAuth2": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title="Secure Agent API",
    description="API with Keycloak OAuth2 authentication in Swagger UI",
    version="1.0.0",
    swagger_ui_init_oauth={
        "clientId": "fastapi-client",
        "usePkceWithAuthorizationCodeGrant": True
    }
)

origins = [
    "http://localhost:5173",  # React dev server
    # Add your production URL as well, when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Or specify ["GET", "POST"] etc.
    allow_headers=["*"],  # Or specify, e.g., ["Authorization", "Content-Type"]
)

app.openapi = custom_openapi


class QueryRequest(BaseModel):
    query: str


@app.post("/query", tags=["Agent"], responses={401: {"description": "Unauthorized"}},
          summary="Ask the secure agent",
          description="Send a natural language query and receive an answer",
          openapi_extra={"security": [{"OAuth2": []}]})
async def query_agent(request: QueryRequest, token: str = Security(oauth2_scheme)):
    user_id = verify_token(token)

    history = get_user_session(user_id)
    history.add_user_message(request.query)

    kernel = Kernel()
    chat_completion = OpenAIChatCompletion(
        api_key=os.getenv("OPENAI_API_KEY"),
        ai_model_id="gpt-4.1",
        service_id="secure-agent",
    )
    kernel.add_service(chat_completion)
    execution_settings = OpenAIChatPromptExecutionSettings()

    result = await chat_completion.get_chat_message_content(
        chat_history=history,
        settings=execution_settings,
        kernel=kernel,
    )

    history.add_message(result)
    return {"response": f"{result}"}


@app.post("/reset", tags=["Agent"], responses={401: {"description": "Unauthorized"}},
          summary="Remove history from agent",
          description="Remove the history of the agent",
          openapi_extra={"security": [{"OAuth2": []}]})
async def reset_session(token: str = Security(oauth2_scheme)):
    user_id = verify_token(token)

    history = get_user_session(user_id)
    history.clear()

    return {"response": f"Hi {user_id}, we removed your history."}
