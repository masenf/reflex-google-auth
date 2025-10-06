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


class TokenResponse(TypedDict, total=False):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str
    id_token: str


class TokenCredential(TypedDict, total=False):
    iss: str
    azp: str
    aud: str
    sub: str
    hd: str
    email: str
    email_verified: bool
    at_hash: str
    nbf: int
    name: str
    picture: str
    given_name: str
    family_name: str
    iat: int
    exp: int
    jti: str


async def get_token(auth_code) -> TokenResponse:
    """Get the token(s) from an auth code.

    Args:
        auth_code: Returned from an 'auth-code' flow.

    Returns:
        The token response, containing access_token, refresh_token and id_token.
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
        return TokenResponse(response_data)


async def get_id_token(auth_code: str) -> str:
    token_data = await get_token(auth_code)
    if "id_token" not in token_data:
        raise ValueError("No id_token in token response")
    return token_data["id_token"]


class GoogleAuthState(rx.State):
    token_response_json: str = rx.LocalStorage()
    refresh_token: str = rx.LocalStorage()

    @rx.var
    def id_token_json(self) -> str:
        """For compatibility only. Use token_response_json instead."""
        try:
            return json.dumps(
                {"credential": json.loads(self.token_response_json).get("id_token", "")}
            )
        except Exception:
            return ""

    @rx.event
    async def on_success(self, response: dict):
        if "code" in response:
            # Handle auth-code flow
            token_response = await get_token(response["code"])
            self.token_response_json = json.dumps(token_response)
            if "refresh_token" in token_response:
                self.refresh_token = token_response["refresh_token"]
        elif "credential" in response:
            # Handle id-token flow
            self.token_response_json = json.dumps({"id_token": response["credential"]})
            self.refresh_token = ""
        else:
            self.token_response_json = ""
            self.refresh_token = ""
            raise ValueError("No code or credential in response")

    @rx.event
    async def refresh_access_token(self):
        try:
            if not self.access_token:
                return  # no token to refresh
            if not self.refresh_token:
                # token not available, must re-auth
                self.token_response_json = ""
                return
            async with AsyncClient() as client:
                response = await client.post(
                    TOKEN_URI,
                    data={
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token",
                    },
                )
                response.raise_for_status()
                new_token_data = response.json()
                # Save the new refresh token if provided
                if "refresh_token" in new_token_data:
                    self.refresh_token = new_token_data["refresh_token"]
                self.token_response_json = json.dumps(new_token_data)
        except Exception as exc:
            print(f"Error refreshing token: {exc!r}")  # noqa: T201

    @rx.var(cache=True)
    def client_id(self) -> str:
        return CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")

    @rx.var
    def scopes(self) -> list[str]:
        try:
            scope_str = json.loads(self.token_response_json).get("scope", "")
            return scope_str.split(" ") if scope_str else []
        except Exception:
            return []

    @rx.var
    def access_token(self) -> str:
        try:
            return json.loads(self.token_response_json).get("access_token", "")
        except Exception:
            return ""

    @rx.var
    def id_token(self) -> str:
        try:
            return json.loads(self.token_response_json).get("id_token", "")
        except Exception:
            return ""

    @rx.var(cache=True)
    def tokeninfo(self) -> TokenCredential:
        try:
            return TokenCredential(
                verify_oauth2_token(
                    self.id_token,
                    requests.Request(),
                    self.client_id,
                )
            )
        except Exception as exc:
            if self.token_response_json:
                print(f"Error verifying token: {exc!r}")  # noqa: T201
                self.token_response_json = ""
        return {}

    @rx.event
    def logout(self):
        self.token_response_json = ""
        self.refresh_token = ""

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
