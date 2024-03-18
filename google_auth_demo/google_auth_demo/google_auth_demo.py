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


app = rx.App()
app.add_page(index)
