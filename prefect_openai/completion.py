from typing import Optional, Dict, Any

from prefect.blocks.core import Block
from prefect_openai import OpenAICredentials
from pydantic import Field
from prefect.utilities.asyncutils import sync_compatible


class CompletionModel(Block):
    """
    A block that contains config for an OpenAI Completion Model.
    """

    openai_credentials: OpenAICredentials = Field(default=..., description="The credentials used to authenticate with OpenAI.")
    model: str = Field(default=..., description="ID of the model to use.")
    temperature: float = Field(default=0.5, description="The temperature of the model.")
    max_tokens: int = Field(default=16, description="The maximum number of tokens to generate.")
    suffix: Optional[str] = Field(default=None, description="The suffix to append to the prompt.")
    echo: bool = Field(default=False, description="Whether to echo the prompt.")
    timeout: Optional[float] = Field(default=None, description="The maximum time to wait for the model to warm up.")

    _block_type_name = "OpenAI Completion Model"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/QE8JwcbZBmIfiognXDLcY/2bcd4c759f877d37159f576101218b49/open-ai-logo-8B9BFEDC26-seeklogo.com.png?h=250"  # noqa

    @sync_compatible
    async def create(self, prompt: str, **acreate_kwargs: Dict[str, Any]) -> str:
        """
        Create a completion.

        Args:
            prompt: The prompt to use for the completion.
            **acreate_kwargs: Additional keyword arguments to pass to `openai.Completion.acreate`.
        
        Returns:
            The completion.
        """
        client = self.openai_credentials.get_client()
        
        input_kwargs = dict(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            suffix=self.suffix, 
            echo=self.echo,
            timeout=self.timeout,
        )
        input_kwargs.update(acreate_kwargs)

        return await client.Completion.acreate(
            prompt=prompt,
            **acreate_kwargs
        )
