from unittest.mock import MagicMock

import httpx
import pytest
from prefect import flow, task

from prefect_openai.completion import CompletionModel, interpret_exception


def test_completion_model_create(mock_openai_credentials: MagicMock):
    completion_model = CompletionModel(
        openai_credentials=mock_openai_credentials, temperature=0.88
    )
    prompt = "what is meaning of meaning"
    completion_model.submit_prompt(prompt)
    mock_openai_credentials._mock_model.acreate.assert_called_once_with(
        prompt="what is meaning of meaning",
        model="text-curie-001",
        temperature=0.88,
        max_tokens=16,
        suffix=None,
        echo=False,
        timeout=None,
    )


def test_completion_model_create_override(mock_openai_credentials: MagicMock):
    completion_model = CompletionModel(
        openai_credentials=mock_openai_credentials, temperature=0.88
    )
    prompt = "what is meaning of meaning"
    completion_model.submit_prompt(prompt, temperature=0.28, max_tokens=8)
    mock_openai_credentials._mock_model.acreate.assert_called_once_with(
        prompt="what is meaning of meaning",
        model="text-curie-001",
        temperature=0.28,
        max_tokens=8,
        suffix=None,
        echo=False,
        timeout=None,
    )


class TestInterpretExceptionNoError:
    @interpret_exception("curie")
    def sync_fn(self, divisor: int):
        return 1 / divisor

    def test_sync_fn(self, mock_openai_credentials):
        assert self.sync_fn(1) == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @pytest.mark.parametrize("return_state", [True, False])
    def test_sync_flow(self, mock_openai_credentials, return_state):
        result = flow(self.sync_fn)(1, return_state=return_state)
        if return_state:
            result = result.result()
        assert result == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @pytest.mark.parametrize("return_state", [True, False])
    def test_sync_task(self, mock_openai_credentials, return_state):
        @flow
        def a_flow():
            return task(self.sync_fn)(1, return_state=return_state)

        result = a_flow()
        if return_state:
            result = result.result()
        assert result == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @interpret_exception("curie")
    async def async_fn(self, divisor: int):
        return 1 / divisor

    async def test_async_fn(self, mock_openai_credentials):
        assert await self.async_fn(1) == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @pytest.mark.parametrize("return_state", [True, False])
    async def test_async_flow(self, mock_openai_credentials, return_state):
        result = await flow(self.async_fn)(1, return_state=return_state)
        if return_state:
            result = await result.result(fetch=True)
        assert result == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @pytest.mark.parametrize("return_state", [True, False])
    async def test_async_task(self, mock_openai_credentials, return_state):
        @flow
        async def a_flow():
            return await task(self.async_fn)(1, return_state=return_state)

        result = await a_flow()
        if return_state:
            result = await result.result(fetch=True)
        assert result == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0


class TestInterpretExceptionError:
    @interpret_exception("curie")
    def sync_fn(self, divisor: int):
        return 1 / divisor

    def test_sync_fn(self, mock_openai_credentials):
        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            self.sync_fn(0)
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
        assert mock_openai_credentials._mock_block_load.call_count == 1

    @pytest.mark.parametrize("return_state", [True, False])
    def test_sync_flow(self, mock_openai_credentials, return_state):
        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            result = flow(self.sync_fn)(0, return_state=return_state)
            if return_state:
                result = result.result()
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
        assert mock_openai_credentials._mock_block_load.call_count == 1

    @pytest.mark.parametrize("return_state", [True, False])
    def test_sync_task(self, mock_openai_credentials, return_state):
        @flow
        def a_flow():
            return task(self.sync_fn)(0, return_state=return_state)

        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            result = a_flow()
            if return_state:
                result = result.result()
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
        assert mock_openai_credentials._mock_block_load.call_count == 1

    @interpret_exception("curie")
    async def async_fn(self, divisor: int):
        return 1 / divisor

    async def test_async_fn(self, mock_openai_credentials):
        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            await self.async_fn(0)
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
        assert mock_openai_credentials._mock_block_load.call_count == 1

    @pytest.mark.parametrize("return_state", [True, False])
    async def test_async_flow(self, mock_openai_credentials, return_state):
        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            result = await (flow(self.async_fn)(0, return_state=return_state))
            if return_state:
                result = await result.result(fetch=True)
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
        assert mock_openai_credentials._mock_block_load.call_count == 1

    @pytest.mark.parametrize("return_state", [True, False])
    async def test_async_task(self, mock_openai_credentials, return_state):
        @flow
        async def a_flow():
            return await task(self.async_fn)(0, return_state=return_state)

        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            result = await a_flow()
            if return_state:
                result = await result.result(fetch=True)
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
        assert mock_openai_credentials._mock_block_load.call_count == 1

    def test_flow_args(self, mock_openai_credentials):
        """
        Test whether flow kwargs are still working.
        """
        my_flow = flow(self.sync_fn, retries=2)
        assert my_flow.retries == 2
        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            my_flow(0)
        # 2 retries + original try == 3
        assert mock_openai_credentials._mock_block_load.call_count == 3

    def test_httpx_error(self, mock_openai_credentials, respx_mock):
        """
        Some errors, like HttpError, have additional args/kwargs to rebuild.
        Specifically keyword-only args.
        """
        respx_mock.get("https://api.openai.com/v1/engines/curie").mock(
            side_effect=httpx.HTTPError("test")
        )

        @interpret_exception("curie")
        def request_web():
            return httpx.get("https://api.openai.com/v1/engines/curie")

        with pytest.raises(httpx.HTTPError, match="\nOpenAI"):
            request_web()

    def test_custom_error(self, mock_openai_credentials):
        """
        Test whether custom exceptions work too.
        """

        class CustomException(Exception):
            def __init__(self, message, arg, keyword="keyword"):
                self.message = message
                self.arg = arg
                self.keyword = keyword

        @interpret_exception("curie")
        def custom_fn():
            raise CustomException("For testing only...", 1, keyword="keyword")

        with pytest.raises(CustomException, match="OpenAI"):
            custom_fn()

    def test_prompt_prefix(self, mock_openai_credentials):
        """
        Test whether the prompt prefix is added.
        """

        @interpret_exception("curie", prompt_prefix="Solution to:")
        def sync_fn(divisor: int):
            return 1 / divisor

        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            sync_fn(0)

        mock_openai_credentials._mock_model.submit_prompt.assert_called_once_with(
            "Solution to: ```\ndivision by zero\n```"
        )

    def test_traceback_tail(self, mock_openai_credentials):
        """
        Test whether the prompt prefix is added.
        """

        @interpret_exception("curie", traceback_tail=1)
        def sync_fn(divisor: int):
            return 1 / divisor

        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            sync_fn(0)

        args_list = mock_openai_credentials._mock_model.submit_prompt.call_args_list[0]
        input_arg = args_list[0][0]
        assert "return 1 / divisor\n\ndivision by zero\n`" in input_arg

    def test_zero_traceback_tail(self, mock_openai_credentials):
        """
        Test whether the prompt prefix is added.
        """

        @interpret_exception("curie", traceback_tail=0)
        def sync_fn(divisor: int):
            return 1 / divisor

        with pytest.raises(ZeroDivisionError, match="\nOpenAI"):
            sync_fn(0)
        mock_openai_credentials._mock_model.submit_prompt.assert_called_once_with(
            "Explain: ```\ndivision by zero\n```"
        )


class TestInterpretExceptionImproperUse:
    def test_flow(self):
        match = "interpret_exception should be nested under the flow / task decorator"
        with pytest.raises(ValueError, match=match):

            @interpret_exception("curie")
            @flow
            def sync_flow(self, divisor: int):
                return 1 / divisor

    def test_task(self):
        match = "interpret_exception should be nested under the flow / task decorator"
        with pytest.raises(ValueError, match=match):

            @interpret_exception("curie")
            @task
            def sync_task(self, divisor: int):
                return 1 / divisor
