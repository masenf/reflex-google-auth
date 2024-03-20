import reflex as rx

from .state import GoogleAuthState


class GoogleOAuthProvider(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleOAuthProvider"

    client_id: rx.Var[str]

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        props.setdefault("client_id", GoogleAuthState.client_id)
        return super().create(*children, **props)


google_oauth_provider = GoogleOAuthProvider.create


class GoogleLogin(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleLogin"

    def get_event_triggers(self):
        return {"on_success": lambda data: [data]}

    @classmethod
    def create(cls, **props) -> "GoogleLogin":
        props.setdefault("on_success", GoogleAuthState.on_success)
        return super().create(**props)


google_login = GoogleLogin.create
