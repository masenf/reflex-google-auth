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


def _on_success_signature(data: rx.Var[dict]) -> tuple[rx.Var[dict]]:
    return data,


class GoogleLogin(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleLogin"

    on_success: rx.EventHandler[_on_success_signature]

    @classmethod
    def create(cls, **props) -> "GoogleLogin":
        props.setdefault("on_success", GoogleAuthState.on_success)
        return super().create(**props)


google_login = GoogleLogin.create
