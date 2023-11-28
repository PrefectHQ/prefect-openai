"""Module for generating and configuring OpenAI images."""
from logging import Logger
from typing import Any, Dict

from openai.openai_object import OpenAIObject
from prefect.blocks.core import Block
from prefect.exceptions import MissingContextError
from prefect.logging.loggers import get_logger, get_run_logger
from prefect.utilities.asyncutils import sync_compatible
from pydantic import VERSION as PYDANTIC_VERSION

if PYDANTIC_VERSION.startswith("2."):
    from pydantic.v1 import Field
else:
    from pydantic import Field

from typing_extensions import Literal

from prefect_openai import OpenAICredentials


class ImageModel(Block):
    """
    A block that contains config for an OpenAI Image Model.
    Learn more in the [OpenAPI Image generation docs](
        https://beta.openai.com/docs/guides/images)

    Attributes:
        openai_credentials: The credentials used to authenticate with OpenAI.
        size: The size of the image to generate.
        n: The number of images to generate.
        response_format: The format of the image to generate.

    Example:
        Load a configured block:
        ```python
        from prefect_openai import ImageModel

        image_model = ImageModel.load("BLOCK_NAME")
        ```
    """

    openai_credentials: OpenAICredentials = Field(
        default=..., description="The credentials used to authenticate with OpenAI."
    )
    size: Literal["256x256", "512x512", "1024x1024"] = Field(
        default="256x256", description="The size of the image to generate."
    )
    n: int = Field(
        default=1,
        title="Number of images",
        description="The number of images to generate.",
    )
    response_format: Literal["url", "b64_json"] = Field(
        default="url", description="The format of the image to generate."
    )

    _block_type_name = "OpenAI Image Model"
    _logo_url = "https://cdn.sanity.io/images/3ugk85nk/production/760539393a7dbf93a143fb01c2a8b0fe7157a8d8-247x250.png"  # noqa

    @property
    def logger(self) -> Logger:
        """
        Returns a logger based on whether the ImageModel
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
        Submits a prompt for the model to generate an image.
        Learn more in the [OpenAPI Image generation docs](
            https://beta.openai.com/docs/guides/images)

        Args:
            prompt: The prompt to use for the image.
            **acreate_kwargs: Additional keyword arguments to pass
                to [`openai.Image.acreate`](
                https://beta.openai.com/docs/api-reference/images/create).

        Returns:
            The OpenAIObject containing the image and associated metadata.

        Example:
            Create an OpenAI Image given a prompt:
            ```python
            from prefect_openai import ImageModel

            image_model = ImageModel.load("BLOCK_NAME")
            image_model.submit_prompt(prompt="A prompt for an image.")
            ```
        """
        client = self.openai_credentials.get_client()

        input_kwargs = dict(
            size=self.size,
            n=self.n,
            response_format=self.response_format,
        )
        input_kwargs.update(acreate_kwargs)
        creation = await client.Image.acreate(prompt=prompt, **input_kwargs)
        self.logger.info(
            f"Finished image completion, creating " f"{self.n} {self.size!r} image(s)."
        )
        return creation
