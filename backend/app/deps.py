from typing import Annotated

from fastapi import Depends, Header


def current_user(
    x_authentik_username: Annotated[str | None, Header()] = None,
) -> str:
    """The authenticated user, from the header Caddy's forward-auth sets.
    Falls back to "local" for dev / direct access (the route is VPN + SSO gated
    upstream regardless)."""
    return x_authentik_username or "local"


CurrentUser = Annotated[str, Depends(current_user)]
