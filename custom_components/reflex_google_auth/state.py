"""Handle Google Auth."""

import json
import os
import time
from typing import TypedDict

import reflex as rx
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from httpx import AsyncClient

TOKEN_URI = "https://oauth2.googleapis.com/token"
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")


def set_client_id(client_id: str):
    """Set the client id."""
    global CLIENT_ID
    CLIENT_ID = client_id


class TokenCredential(TypedDict, total=False):
    iss: str
    azp: str
    aud: str
    sub: str
    hd: str
    email: str
    email_verified: bool
    nbf: int
    name: str
    picture: str
    given_name: str
    family_name: str
    iat: int
    exp: int
    jti: str


async def get_id_token(auth_code) -> str:
    """Get the id token credential from an auth code.

    Args:
        auth_code: Returned from an 'auth-code' flow.

    Returns:
        The id token credential.
    """
    async with AsyncClient() as client:
        response = await client.post(
            TOKEN_URI,
            data={
                "code": auth_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("id_token")


class GoogleAuthState(rx.State):
    id_token_json: str = rx.LocalStorage()

    @rx.event
    async def on_success(self, id_token: dict):
        if "code" in id_token:
            # Handle auth-code flow
            id_token["credential"] = await get_id_token(id_token["code"])
        self.id_token_json = json.dumps(id_token)

    @rx.var(cache=True)
    def client_id(self) -> str:
        return CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")

    @rx.var(cache=True)
    def tokeninfo(self) -> TokenCredential:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)["credential"],
                requests.Request(),
                self.client_id,
            )
        except Exception as exc:
            if self.id_token_json:
                print(f"Error verifying token: {exc!r}")  # noqa: T201
                self.id_token_json = ""
        return {}

    @rx.event
    def logout(self):
        self.id_token_json = ""

    @rx.var(cache=False)
    def token_is_valid(self) -> bool:
        try:
            return bool(
                self.tokeninfo and int(self.tokeninfo.get("exp", 0)) > time.time()
            )
        except Exception:
            return False

    @rx.var(cache=True)
    def user_name(self) -> str:
        return self.tokeninfo.get("name", "")

    @rx.var(cache=True)
    def user_email(self) -> str:
        return self.tokeninfo.get("email", "")
