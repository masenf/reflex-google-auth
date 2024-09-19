"""Handle Google Auth."""

import json
import os
import time

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import reflex as rx


CLIENT_ID = None


def set_client_id(client_id: str):
    """Set the client id."""
    global CLIENT_ID
    CLIENT_ID = client_id


class GoogleAuthState(rx.State):
    id_token_json: str = rx.LocalStorage()

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)

    @rx.var(cache=True)
    def client_id(self) -> str:
        return CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")

    @rx.var(cache=True)
    def tokeninfo(self) -> dict[str, str]:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)["credential"],
                requests.Request(),
                self.client_id,
            )
        except Exception as exc:
            if self.id_token_json:
                print(f"Error verifying token: {exc}")
        return {}

    def logout(self):
        self.id_token_json = ""

    @rx.var
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
