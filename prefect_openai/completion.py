"""Module for generating and configuring OpenAI completions."""
from logging import Logger
from typing import Any, Dict, Optional

from openai.openai_object import OpenAIObject
from prefect.blocks.core import Block
from prefect.exceptions import MissingContextError
from prefect.logging.loggers import get_logger, get_run_logger
from prefect.utilities.asyncutils import sync_compatible
from pydantic import Field

from prefect_openai import OpenAICredentials


class CompletionModel(Block):
    """
    A block that contains config for an OpenAI Completion Model.

    Attributes:
        openai_credentials: The credentials used to authenticate with OpenAI.
        model: ID of the model to use.
        temperature: The temperature of the model.
        max_tokens: The maximum number of tokens to generate.
        suffix: The suffix to append to the prompt.
        echo: Whether to echo the prompt.
        timeout: The maximum time to wait for the model to warm up.

    Example:
        Load a configured block:
        ```python
        from prefect_openai import CompletionModel

        completion_model = CompletionModel.load("BLOCK_NAME")
        ```
    """

    openai_credentials: OpenAICredentials = Field(
        default=..., description="The credentials used to authenticate with OpenAI."
    )
    model: str = Field(default="text-curie-001", description="ID of the model to use.")
    temperature: float = Field(default=0.5, description="The temperature of the model.")
    max_tokens: int = Field(
        default=16, description="The maximum number of tokens to generate."
    )
    suffix: Optional[str] = Field(
        default=None, description="The suffix to append to the prompt."
    )
    echo: bool = Field(default=False, description="Whether to echo the prompt.")
    timeout: Optional[float] = Field(
        default=None, description="The maximum time to wait for the model to warm up."
    )

    _block_type_name = "OpenAI Completion Model"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/QE8JwcbZBmIfiognXDLcY/2bcd4c759f877d37159f576101218b49/open-ai-logo-8B9BFEDC26-seeklogo.com.png?h=250"  # noqa

    @property
    def logger(self) -> Logger:
        """
        Returns a logger based on whether the CompletionModel
        is called from within a flow or task run context.
        If a run context is present, the logger property returns a run logger.
        Else, it returns a default logger labeled with the class's name.
        Returns:
            The run logger or a default logger with the class's name.
        """
        try:
            return get_run_logger()
        except MissingContextError:
            return get_logger(self.__class__.__name__)

    @sync_compatible
    async def submit_prompt(
        self, prompt: str, **acreate_kwargs: Dict[str, Any]
    ) -> OpenAIObject:
        """
        Submits a prompt for the model to generate a text completion.
        OpenAI will return an object potentially containing multiple `choices`,
        where the zeroth index is what they consider the "best" completion.
        Learn more in the [OpenAPI Text Completion docs](
            https://beta.openai.com/docs/guides/completion)

        Args:
            prompt: The prompt to use for the completion.
            **acreate_kwargs: Additional keyword arguments to pass
                to [`openai.Completion.acreate`](
                https://beta.openai.com/docs/api-reference/completions/create).

        Returns:
            The OpenAIObject containing the completion and associated metadata.

        Example:
            Create an OpenAI Completion given a prompt:
            ```python
            from prefect import flow
            from prefect_openai import CompletionModel, OpenAICredentials

            @flow(log_prints=True)
            def my_ai_bot(model_name: str = "text-davinci-003")
                credentials = OpenAICredentials.load("my-openai-creds")

                completion_model = CompletionModel(
                    openai_credentials=credentials,
                )

                for prompt in ["hi!", "what is the meaning of life?"]:
                    completion = completion_model.submit_prompt(prompt)
                    print(completion.choices[0].text)
            ```
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

        creation = await client.Completion.acreate(prompt=prompt, **input_kwargs)
        total_tokens = creation.usage["total_tokens"]
        num_choices = len(creation.choices)
        self.logger.info(
            f"Finished text completion using the {self.model!r} "
            f"model with {total_tokens} tokens, creating {num_choices} choice(s)."
        )
        return creation
