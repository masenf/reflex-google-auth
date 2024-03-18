"""Handle Google Auth."""

import json
import time

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import reflex as rx

from . import google_auth


class GoogleAuthState(rx.State):
    id_token_json: str = rx.LocalStorage()

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)

    @rx.cached_var
    def tokeninfo(self) -> dict[str, str]:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)["credential"],
                requests.Request(),
                google_auth.CLIENT_ID,
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

    @rx.cached_var
    def user_name(self) -> str:
        return self.tokeninfo.get("name", "")

    @rx.cached_var
    def user_email(self) -> str:
        return self.tokeninfo.get("email", "")
