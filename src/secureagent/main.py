import logging
import os

from dotenv import load_dotenv
from fastapi import Security
from pydantic import BaseModel
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.openapi_plugin import OpenAPIFunctionExecutionParameters

from .logging_config import setup_logging

load_dotenv()

from .app_factory import create_app, oauth2_scheme
from .session import get_user_session
from .auth import verify_token

setup_logging()
app_logger = logging.getLogger("app")

app = create_app(
    title="Secure Agent API",
    description="API with Keycloak OAuth2 authentication in Swagger UI",
    version="1.0.0",
    origins=["http://localhost:5173"]
)


class QueryRequest(BaseModel):
    query: str


@app.post("/query", tags=["Agent"], responses={401: {"description": "Unauthorized"}},
          summary="Ask the secure agent",
          description="Send a natural language query and receive an answer")
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
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    async def add_bearer_token(**kwargs):
        return {"Authorization": f"Bearer {token}"}

    kernel.add_plugin_from_openapi(
        plugin_name="hr",
        openapi_document_path="http://localhost:8001/openapi.json",
        execution_settings=OpenAPIFunctionExecutionParameters(
            enable_payload_namespacing=True,
            auth_callback=add_bearer_token,
            server_url_override="http://localhost:8001",
        ),
    )

    result = await chat_completion.get_chat_message_content(
        chat_history=history,
        settings=execution_settings,
        kernel=kernel,
    )

    history.add_message(result)
    return {"response": f"{result}"}


@app.post("/reset", tags=["Agent"], responses={401: {"description": "Unauthorized"}},
          summary="Remove history from agent",
          description="Remove the history of the agent")
async def reset_session(token: str = Security(oauth2_scheme)):
    user_id = verify_token(token)

    history = get_user_session(user_id)
    history.clear()

    return {"response": f"Hi {user_id}, we removed your history."}
