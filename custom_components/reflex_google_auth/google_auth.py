from typing import cast

import reflex as rx
from reflex.event import EventType

from .state import GoogleAuthState

LIBRARY = "@react-oauth/google"


class GoogleOAuthProvider(rx.Component):
    library = LIBRARY
    tag = "GoogleOAuthProvider"

    client_id: rx.Var[str]

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        props.setdefault("client_id", GoogleAuthState.client_id)
        return super().create(*children, **props)


google_oauth_provider = GoogleOAuthProvider.create


def _on_success_signature(data: rx.Var[dict]) -> tuple[rx.Var[dict]]:
    return (data,)


class GoogleLogin(rx.Component):
    library = LIBRARY
    tag = "GoogleLogin"

    on_success: rx.EventHandler[_on_success_signature]

    @classmethod
    def create(cls, **props) -> "GoogleLogin":
        props.setdefault("on_success", GoogleAuthState.on_success)
        return cast("GoogleLogin", super().create(**props))


google_login = GoogleLogin.create


def handle_google_login(
    on_success: EventType[dict] = GoogleAuthState.on_success,
) -> rx.Var[rx.EventChain]:
    on_success_event_chain = rx.Var.create(
        rx.EventChain.create(
            value=on_success,  # type: ignore
            args_spec=_on_success_signature,
            key="on_success",
        )
    )
    return rx.Var(
        "() => login()",
        _var_type=rx.EventChain,
        _var_data=rx.vars.VarData(
            hooks={
                """
const login = useGoogleLogin({
  onSuccess: %s,
  flow: 'auth-code',
});"""
                % on_success_event_chain: on_success_event_chain._get_all_var_data(),
            },
            imports={LIBRARY: "useGoogleLogin"},
        ),
    )
