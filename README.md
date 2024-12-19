# google-auth

Sign in with Google.

## Installation

```bash
pip install reflex-google-auth
```

## Usage

### Create Google OAuth2 Client ID

Head over to https://console.developers.google.com/apis/credentials and sign in with the Google account that should manage the app and credential tokens.

- Click "Create Project" and give it a name. After creation the new project should be selected.
- Click "Configure Consent Screen", Choose "External", then Create.
  - Enter App Name and User Support Email -- these will be shown to users when logging in
  - Scroll all the way down to "Developer contact information" and add your email address, click "Save and Continue"
  - Click "Add or Remove Scopes"
    - Select "Email", "Profile", and "OpenID Connect"
    - Click "Update", then "Save and Continue"
  - Add any test users that should be able to log in during development.
- From the "Credentials" page, click "+ Create Credentials", then "OAuth client ID"
  - Select Application Type: "Web Application"
  - Add Authorized Javascript Origins: http://localhost, http://localhost:3000, https://example.com (prod domain must be HTTPS)
  - If using custom button, add the same origins to "Authorized redirect URIs"
  - Click "Save"
- Copy the OAuth "Client ID" and "Client Secret" and save it for later. Mine looks like 309209880368-4uqd9e44h7t4alhhdqn48pvvr63cc5j5.apps.googleusercontent.com

https://github.com/reflex-dev/reflex-examples/assets/1524005/af2499a6-0bda-4d60-b52b-4f51b7322fd5

### Configure Environment Variables

Set the following environment variables based on your deployment.

```bash
export GOOGLE_CLIENT_ID="309209880368-4uqd9e44h7t4alhhdqn48pvvr63cc5j5.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your_client_secret"
export GOOGLE_REDIRECT_URI="http://localhost:3000"
```

### Integrate with Reflex app

The `GoogleAuthState` provided by this component has a `token_is_valid` var that
should be checked before returning any protected content.

Additionally the `GoogleAuthState.tokeninfo` dict contains the user's profile information.

```python
from reflex_google_auth import GoogleAuthState, require_google_login


class State(GoogleAuthState):
    @rx.var(cache=True)
    def protected_content(self) -> str:
        if self.token_is_valid:
            return f"This content can only be viewed by a logged in User. Nice to see you {self.tokeninfo['name']}"
        return "Not logged in."
```

The convenience decorator, `require_google_login`, can wrap an existing component, and
show the "Sign in with Google" button if the user is not already authenticated. It can be
used on a page function or any subcomponent function of the page.

The "Sign in with Google" button can also be displayed via `google_login()`:

```python
from reflex_google_auth import google_login, google_oauth_provider

def page():
    return rx.div(
        google_oauth_provider(
            google_login(),
        ),
    )
```

To uniquely identify a user, the `GoogleAuthState.tokeninfo['sub']` field can be used.

See the example in
[masenf/rx_shout](https://github.com/masenf/rx_shout/blob/main/rx_shout/state.py)
for how to integrate an authenticated Google user with other app-specific user
data.

### Customizing the Button

If you want to use your own login button, you may use whatever component you
like, as long as it is wrapped in a `reflex_google_auth.google_oauth_provider`
component and the `on_click` triggers
`reflex_google_auth.handle_google_login()`. Note that this cannot be combined
with other event handlers.

This functionality is also exposed in the `require_google_auth` decorator, which
accepts a `button` keyword argument.

When using a custom button, the returned auth-code _must be validated on the
backend_, which is handled by this library, but **requires additionally setting
`GOOGLE_CLIENT_SECRET` and `GOOGLE_REDIRECT_URI` environment variables**. These
can be configured in the Google Cloud Console as described above.

```python
from reflex_google_auth import handle_google_login, require_google_login, GoogleAuthState


@require_google_login(button=rx.button("Google Login 🚀", on_click=handle_google_login()))
def custom_button() -> rx.Component:
    return rx.vstack(
        f"{GoogleAuthState.tokeninfo['email']} clicked a custom button to login, nice",
    )
```