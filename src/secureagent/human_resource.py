import logging
from dotenv import load_dotenv
from fastapi import Security, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from .logging_config import setup_logging

load_dotenv()

from .app_factory import oauth2_scheme, create_app
from .auth import verify_token

setup_logging()
app_logger = logging.getLogger("app")
app_logger.info("Starting HR Agent API")

# Initialize the FastAPI app with CORS middleware
app = create_app(
    title="HR Agent API",
    description="Agent giving access to HR related functions like requesting number of days of still available.",
    version="1.0.0",
    origins=["http://localhost:8000", "http://localhost:5173"]
)

days_off_db = {
    "jettro": 10,
    "johndoe": 5,
}

class DaysOffRequest(BaseModel):
    """
    Request model for querying the number of days off for a specific person.
    """
    person_name: str = Field(..., title="Person name", description="The name of the person whose days off are being requested.")


@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    body = await request.body()
    app_logger.debug(f"Request path: {request.url.path}")
    app_logger.debug(f"Request headers: {dict(request.headers)}")
    app_logger.debug(f"Request body: {body.decode('utf-8') if body else '<empty>'}")
    response = await call_next(request)
    return response


@app.post("/daysOff", tags=["HR"], responses={401: {"description": "Unauthorized"}},
          summary="Returns number of days off you have left.",
          description="Uses the user in the token to determine the available days off.")
async def days_off(token: str = Security(oauth2_scheme)):
    app_logger.info("Received request to get days off.")
    user_id = verify_token(token)

    if user_id not in days_off_db:
        raise HTTPException(status_code=400, detail="User not found in database.")

    return {"days_off_available": days_off_db[user_id]}  # Placeholder value, replace with actual logic


@app.post("/daysOffFor", tags=["HR"], responses={401: {"description": "Unauthorized"}},
          summary="Returns number of days off for the specified user.",
          description="Uses the provided user to determine the available days off.")
async def days_off_for(days_off_request: DaysOffRequest, token: str = Security(oauth2_scheme)):
    user_id = verify_token(token, requested_role="office_management")
    person_name = days_off_request.person_name

    if person_name not in days_off_db:
        raise HTTPException(status_code=400, detail=f"{person_name} not found in database.")

    return {"days_off_available": days_off_db[person_name], "person_name": person_name, "asked_by": user_id}
