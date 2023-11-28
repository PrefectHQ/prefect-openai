"""Module for generating and configuring OpenAI completions."""
import functools
import inspect
import traceback
from logging import Logger
from typing import Any, Callable, Dict, Optional, Tuple, Union

from openai.openai_object import OpenAIObject
from prefect.blocks.core import Block
from prefect.exceptions import MissingContextError
from prefect.flows import Flow
from prefect.logging.loggers import get_logger, get_run_logger
from prefect.tasks import Task
from prefect.utilities.asyncutils import is_async_fn, sync_compatible
from pydantic import VERSION as PYDANTIC_VERSION

if PYDANTIC_VERSION.startswith("2."):
    from pydantic.v1 import Field
else:
    from pydantic import Field

from typing_extensions import Literal

from prefect_openai import OpenAICredentials


class CompletionModel(Block):
    """
    A block that contains config for an OpenAI Completion Model.
    Learn more in the [OpenAPI Text Completion docs](
        https://beta.openai.com/docs/guides/completion)

    Attributes:
        openai_credentials: The credentials used to authenticate with OpenAI.
        model: ID of the model to use.
        temperature: What sampling temperature to use.
            Higher values means the model will take more risks.
            Try 0.9 for more creative applications, and 0 (argmax sampling)
            for ones with a well-defined answer.
        max_tokens: The maximum number of tokens to generate in the completion.
            The token count of your prompt plus max_tokens cannot exceed the
            model's context length. Most models have a context length of 2048 tokens
            (except for the newest models, which support 4096).
        suffix: The suffix to append to the prompt.
        echo: Echo back the prompt in addition to the completion.
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
    model: Union[
        Literal[
            "text-davinci-003", "text-curie-001", "text-babbage-001", "text-ada-001"
        ],
        str,
    ] = Field(default="text-curie-001", description="ID of the model to use.")
    temperature: float = Field(
        default=0.5,
        description=(
            "What sampling temperature to use. Higher values means the model will take "
            "more risks. Try 0.9 for more creative applications, and 0 "
            "(argmax sampling) for ones with a well-defined answer."
        ),
    )
    max_tokens: int = Field(
        default=16,
        description=(
            "The maximum number of tokens to generate in the completion. "
            "The token count of your prompt plus max_tokens cannot exceed the "
            "model's context length. Most models have a context length of 2048 tokens "
            "(except for the newest models, which support 4096)."
        ),
    )
    suffix: Optional[str] = Field(
        default=None, description="The suffix to append to the prompt."
    )
    echo: bool = Field(default=False, description="Whether to echo the prompt.")
    timeout: Optional[float] = Field(
        default=None, description="The maximum time to wait for the model to warm up."
    )

    _block_type_name = "OpenAI Completion Model"
    _logo_url = "https://cdn.sanity.io/images/3ugk85nk/production/760539393a7dbf93a143fb01c2a8b0fe7157a8d8-247x250.png"  # noqa
    _documentation_url = "https://prefecthq.github.io/prefect-openai/completion/#prefect_openai.completion.CompletionModel"  # noqa

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


@sync_compatible
async def _raise_interpreted_exc(
    block_name: str, prompt_prefix: str, traceback_tail: int, exc: Exception
):
    """
    Helper function for reuse so that this doesn't get repeated for sync/async flavors.
    """
    try:
        # gather args and kwargs from the original exception to rebuild
        exc_type = type(exc)
        exc_traceback = exc.__traceback__
        args = exc.args[1:]  # first arg is message, which we're overwriting
        try:
            signature = inspect.signature(exc_type)
            kwargs = {
                param.name: getattr(exc, param.name, None)
                for param in signature.parameters.values()
                if param.kind == param.KEYWORD_ONLY
            }
        except ValueError:
            # no signature available like ZeroDivisionError
            kwargs = {}

        # create a new message
        completion_model = await CompletionModel.load(block_name)
        if traceback_tail > 0:
            traceback_lines = "".join(
                traceback.format_tb(exc.__traceback__)[-traceback_tail:]
            )
            exc_input = f"{traceback_lines}\n{exc}"
        else:
            exc_input = str(exc)
        prompt = f"{prompt_prefix} ```\n{exc_input}\n```"
        response = await completion_model.submit_prompt(prompt)
        interpretation = f"{response.choices[0].text.strip()}"
        new_exc_msg = f"{exc}\nOpenAI: {interpretation}"

        # push the original traceback to the tail so it's not obscured by
        # the additional logic in this except clause
        raise exc_type(new_exc_msg, *args, **kwargs).with_traceback(exc_traceback)
    except Exception:
        # if anything unexpected goes wrong, just raise the original exception
        raise


def interpret_exception(
    completion_model_name: str, prompt_prefix: str = "Explain:", traceback_tail: int = 0
) -> Callable:
    """
    Use OpenAI to interpret the exception raised from the decorated function.
    If used with a flow and return_state=True, will override the original state's
    data and message with the OpenAI interpretation.

    Args:
        completion_model_name: The name of the CompletionModel
            block to use to interpret the caught exception.
        prompt_prefix: The prefix to include in the prompt ahead of the traceback
            and exception message.
        traceback_tail: The number of lines of the original traceback to include
            in the prompt to OpenAI, starting from the tail. If 0, only include the
            exception message in the prompt. Note this can be costly in terms of tokens
            so be sure to set this and the max_tokens in CompletionModel appropriately.

    Returns:
        A decorator that will use an OpenAI CompletionModel to interpret the exception
            raised from the decorated function.

    Examples:
        Interpret the exception raised from a flow.
        ```python
        import httpx
        from prefect import flow
        from prefect_openai.completion import interpret_exception

        @flow
        @interpret_exception("COMPLETION_MODEL_BLOCK_NAME_PLACEHOLDER")
        def example_flow():
            resp = httpx.get("https://httpbin.org/status/403")
            resp.raise_for_status()

        example_flow()
        ```

        Use a unique prefix and include the last line of the traceback in the prompt.
        ```python
        import httpx
        from prefect import flow
        from prefect_openai.completion import interpret_exception

        @flow
        @interpret_exception(
            "COMPLETION_MODEL_BLOCK_NAME_PLACEHOLDER",
            prompt_prefix="Offer a solution:",
            traceback_tail=1,
        )
        def example_flow():
            resp = httpx.get("https://httpbin.org/status/403")
            resp.raise_for_status()

        example_flow()
        ```
    """

    def decorator(fn: Callable) -> Callable:
        """
        The actual decorator.
        """
        if isinstance(fn, (Flow, Task)):
            raise ValueError(
                "interpret_exception should be nested under the flow / task decorator, "
                "e.g. `@flow` -> `@interpret_exception('curie')` -> `def function()`"
            )

        @functools.wraps(fn)
        def sync_wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
            """
            The sync version of the wrapper function that will execute the function.
            """
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                _raise_interpreted_exc(
                    completion_model_name, prompt_prefix, traceback_tail, exc
                )

        # couldn't get sync_compatible working so had to define an async flavor
        @functools.wraps(fn)
        async def async_wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
            """
            The async version of the wrapper function that will execute the function.
            """
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                await _raise_interpreted_exc(
                    completion_model_name, prompt_prefix, traceback_tail, exc
                )

        wrapper = async_wrapper if is_async_fn(fn) else sync_wrapper
        return wrapper

    return decorator
