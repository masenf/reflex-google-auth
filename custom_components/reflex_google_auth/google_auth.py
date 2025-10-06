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
    scope: str | list[str] | rx.Var[str] | rx.Var[list[str]] = "openid profile email",
    on_success: EventType[dict] = GoogleAuthState.on_success,
) -> rx.Var[rx.EventChain]:
    """Create a login event chain to handle Google login.

    Args:
        scope: The space-separated OAuth scopes to request (default "openid profile email").
        on_success: The event to call on successful login (default GoogleAuthState.on_success).

    Returns:
        An event chain that handles the login process.
    """
    on_success_event_chain = rx.Var.create(
        rx.EventChain.create(
            value=on_success,  # type: ignore
            args_spec=_on_success_signature,
            key="on_success",
        )
    )
    scope = rx.Var.create(scope) if not isinstance(scope, rx.Var) else scope
    if isinstance(scope, rx.vars.ArrayVar):
        scope = scope.join(" ")
    return rx.Var(
        "() => login()",
        _var_type=rx.EventChain,
        _var_data=rx.vars.VarData(
            hooks={
                """
const login = useGoogleLogin({
  onSuccess: %s,
  flow: 'auth-code',
  scope: %s,
});"""
                % (on_success_event_chain, scope): rx.vars.VarData.merge(
                    on_success_event_chain._get_all_var_data(),
                    scope._get_all_var_data(),
                ),
            },
            imports={LIBRARY: "useGoogleLogin"},
        ),
    )
