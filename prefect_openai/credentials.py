"""This is an example blocks module"""

import openai
from prefect.blocks.abstract import CredentialsBlock
from pydantic import Field, SecretStr


class OpenAICredentials(CredentialsBlock):
    """
    Credentials used to authenticate with OpenAI.

    Attributes:
        token: The token used to authenticate with OpenAI.

    Example:
        Load a stored value:
        ```python
        from prefect_openai import OpenAICredentials

        credentials = OpenAICredentials.load("BLOCK_NAME")
        ```
    """

    _block_type_name = "OpenAI Credentials"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/QE8JwcbZBmIfiognXDLcY/2bcd4c759f877d37159f576101218b49/open-ai-logo-8B9BFEDC26-seeklogo.com.png?h=250"  # noqa

    token: SecretStr = Field(default=..., description="The token used to authenticate with OpenAI.")

    def get_client(self):
        openai.api_key = self.token.get_secret_value()
        return openai