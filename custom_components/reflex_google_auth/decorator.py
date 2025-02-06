import functools
from typing import Callable, overload

import reflex as rx

from . import google_auth
from .state import GoogleAuthState

ComponentCallable = Callable[[], rx.Component]


@overload
def require_google_login(
    page: ComponentCallable,
) -> ComponentCallable: ...


@overload
def require_google_login() -> Callable[[ComponentCallable], ComponentCallable]: ...


@overload
def require_google_login(
    *,
    button: rx.Component | None,
) -> Callable[[ComponentCallable], ComponentCallable]: ...


def require_google_login(
    page: ComponentCallable | None = None,
    *,
    button: rx.Component | None = None,
) -> ComponentCallable | Callable[[ComponentCallable], ComponentCallable]:
    """Decorator to require Google login before rendering a page.

    The login button should have on_click set to `reflex_google_auth.handle_google_login`.

    Args:
        page: Page to render after Google login.
        button: Button to render if Google login is required.

    Returns:
        A decorator function or the decorated page.
    """

    if button is None:
        button = google_auth.google_login()

    def _inner(page: Callable[[], rx.Component]) -> Callable[[], rx.Component]:
        @functools.wraps(page)
        def _auth_wrapper() -> rx.Component:
            return google_auth.google_oauth_provider(
                rx.cond(
                    rx.State.is_hydrated,
                    rx.cond(
                        GoogleAuthState.token_is_valid,
                        page(),
                        button,
                    ),
                ),
            )

        _auth_wrapper.__name__ = page.__name__

        return _auth_wrapper

    if page is None:
        return _inner
    return _inner(page=page)
