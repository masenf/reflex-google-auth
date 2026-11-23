# Changelog

Notable changes to `reflex-google-auth`.

New entries are added by [towncrier](https://towncrier.readthedocs.io/) from the
news fragments under `news/` — see [Releasing](README.md#releasing). Everything
below `v0.2.0` was reconstructed from the git history after the fact, so it
summarizes each release rather than reproducing entries that were never
written; alpha releases are omitted.

<!-- towncrier release notes start -->

## v0.2.0 (2025-10-13)

### Features

- `handle_google_login` accepts a `scope` parameter, so the `auth-code` flow can request additional Google API scopes and obtain an access token usable on behalf of the signed-in user. The demo app shows reading and writing app data in the user's Google Drive. ([#13](https://github.com/masenf/reflex-google-auth/issues/13))

## v0.1.1 (2025-03-17)

### Features

- Expose the decoded ID token as the `TokenCredential` `TypedDict`, so the fields of `GoogleAuthState.tokeninfo` are typed Reflex Vars. ([#11](https://github.com/masenf/reflex-google-auth/issues/11))

## v0.1.0 (2025-02-05)

### Breaking Changes

- Require `reflex>=0.7.0`. ([#7](https://github.com/masenf/reflex-google-auth/issues/7))
- Require Python 3.10 or newer, up from 3.8.

### Features

- Derive the package version from git tags with `setuptools-scm` instead of hard-coding it in `pyproject.toml`. ([#9](https://github.com/masenf/reflex-google-auth/issues/9))

### Miscellaneous

- Run ruff and pyright from pre-commit, and check them on every pull request. ([#8](https://github.com/masenf/reflex-google-auth/issues/8))
- Publish to PyPI and deploy the demo app to Reflex Cloud when a GitHub release is published. ([#10](https://github.com/masenf/reflex-google-auth/issues/10))

## v0.0.8 (2024-12-19)

### Breaking Changes

- Require `reflex>=0.6.6`. ([#6](https://github.com/masenf/reflex-google-auth/issues/6))

### Features

- Support Google's `auth-code` flow through `handle_google_login`, so any component can trigger sign-in instead of the stock Google button. The returned code is validated on the backend, which requires the `GOOGLE_CLIENT_SECRET` and `GOOGLE_REDIRECT_URI` environment variables. `require_google_login` takes a `button` argument to use a custom button. ([#6](https://github.com/masenf/reflex-google-auth/issues/6))

## v0.0.7 (2024-12-16)

### Bug Fixes

- Annotate the `on_success` event trigger of `google_login` with its argument type. ([#5](https://github.com/masenf/reflex-google-auth/issues/5))

## v0.0.6 (2024-09-19)

### Bug Fixes

- Replace `rx.cached_var`, deprecated in Reflex 0.6.0, with `rx.var(cache=True)`. ([#4](https://github.com/masenf/reflex-google-auth/issues/4))

## v0.0.5 (2024-04-10)

### Documentation

- Document setup and usage in the README and update the project description. Packaging-only release; the code is identical to v0.0.4.

## v0.0.4 (2024-04-01)

### Bug Fixes

- Declare the `on_success` event trigger with the `rx.EventHandler` annotation syntax, and require `reflex>=0.4.6`.

## v0.0.3 (2024-03-19)

### Bug Fixes

- Read the Google client ID in `GoogleAuthState` at runtime instead of baking it in at compile time, so a static frontend export no longer needs `GOOGLE_CLIENT_ID` set.

## v0.0.2 (2024-03-18)

First tagged release.

### Features

- Sign in with Google for Reflex apps: `google_oauth_provider` and `google_login` render the Google sign-in button, `require_google_login` guards a page behind it, and `GoogleAuthState` validates the returned ID token and exposes its claims as `tokeninfo`.
