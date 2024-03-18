import os

import reflex as rx


CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")


def set_client_id(client_id: str):
    """Set the client id."""
    global CLIENT_ID
    CLIENT_ID = client_id


class GoogleOAuthProvider(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleOAuthProvider"

    client_id: rx.Var[str]

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        props.setdefault("client_id", CLIENT_ID)
        return super().create(*children, **props)


google_oauth_provider = GoogleOAuthProvider.create


class GoogleLogin(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleLogin"

    def get_event_triggers(self):
        return {"on_success": lambda data: [data]}

    @classmethod
    def create(cls, **props) -> "GoogleLogin":
        from .state import GoogleAuthState

        props.setdefault("on_success", GoogleAuthState.on_success)
        return super().create(**props)


google_login = GoogleLogin.create
