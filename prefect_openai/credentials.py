"""This is an example blocks module"""

from types import ModuleType

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

    api_key: SecretStr = Field(
        default=...,
        title="API Key",
        description="The API key used to authenticate with OpenAI.",
    )

    def get_client(self) -> ModuleType:
        """
        Gets the OpenAPI client.

        Returns:
            The OpenAPI client.
        """
        openai.api_key = self.api_key.get_secret_value()
        return openai
