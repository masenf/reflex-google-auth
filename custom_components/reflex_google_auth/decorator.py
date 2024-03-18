import functools

import reflex as rx

from . import google_auth
from .state import GoogleAuthState


def require_google_login(page) -> rx.Component:
    @functools.wraps(page)
    def _auth_wrapper() -> rx.Component:
        return google_auth.google_oauth_provider(
            rx.cond(
                rx.State.is_hydrated,
                rx.cond(
                    GoogleAuthState.token_is_valid,
                    page(),
                    google_auth.google_login(),
                ),
            ),
        )

    _auth_wrapper.__name__ = page.__name__

    return _auth_wrapper
