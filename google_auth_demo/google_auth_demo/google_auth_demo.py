import reflex as rx

from reflex_google_auth import GoogleAuthState, require_google_login


class State(GoogleAuthState):
    @rx.cached_var
    def protected_content(self) -> str:
        if self.token_is_valid:
            return f"This content can only be viewed by a logged in User. Nice to see you {self.tokeninfo['name']}"
        return "Not logged in."


def user_info(tokeninfo: dict) -> rx.Component:
    return rx.hstack(
        rx.avatar(
            src=tokeninfo["picture"],
            fallback=tokeninfo["name"],
            size="5",
        ),
        rx.vstack(
            rx.heading(tokeninfo["name"], size="6"),
            rx.text(tokeninfo["email"]),
            align_items="flex-start",
        ),
        rx.button("Logout", on_click=GoogleAuthState.logout),
        padding="10px",
    )


def index():
    return rx.vstack(
        rx.heading("Google OAuth", size="8"),
        rx.link("Protected Page", href="/protected"),
        rx.link("Partially Protected Page", href="/partially-protected"),
        align="center",
    )


@rx.page(route="/protected")
@require_google_login
def protected() -> rx.Component:
    return rx.vstack(
        user_info(GoogleAuthState.tokeninfo),
        rx.text(State.protected_content),
        rx.link("Home", href="/"),
    )


@require_google_login
def user_name_or_sign_in():
    return rx.heading(GoogleAuthState.tokeninfo["name"], size="6")


@rx.page(route="/partially-protected")
def partially_protected() -> rx.Component:
    return rx.vstack(
        rx.heading("This page is partially protected."),
        rx.text(
            "If you are signed in with google, you should see your name below, otherwise "
            "you will see a sign in button",
        ),
        user_name_or_sign_in(),
    ),


app = rx.App()
app.add_page(index)
