"""Module for authenticating with OpenAI."""

from types import ModuleType
from typing import Optional

import openai
from prefect.blocks.abstract import CredentialsBlock
from pydantic import Field, SecretStr


class OpenAICredentials(CredentialsBlock):
    """
    Credentials used to authenticate with OpenAI.

    Attributes:
        api_key: The API key used to authenticate with OpenAI.

    Example:
        Load a configured block:
        ```python
        from prefect_openai import OpenAICredentials

        credentials = OpenAICredentials.load("BLOCK_NAME")
        ```
    """

    _block_type_name = "OpenAI Credentials"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/QE8JwcbZBmIfiognXDLcY/2bcd4c759f877d37159f576101218b49/open-ai-logo-8B9BFEDC26-seeklogo.com.png?h=250"  # noqa
    _documentation_url = "https://prefecthq.github.io/prefect-openai/credentials/#prefect_openai.credentials.OpenAICredentials"  # noqa

    api_key: SecretStr = Field(
        default=...,
        title="API Key",
        description="The API key used to authenticate with OpenAI.",
    )

    organization: Optional[str] = Field(
        default=None,
        title="Organization",
        description="Specify which organization is used for an API request.",
    )

    def get_client(self) -> ModuleType:
        """
        Gets the OpenAPI client.

        Returns:
            The OpenAPI client.
        """
        openai.api_key = self.api_key.get_secret_value()
        openai.organization = self.organization
        return openai
