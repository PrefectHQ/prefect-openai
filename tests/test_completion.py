from unittest.mock import MagicMock

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
            result = result.result()
        assert result == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @pytest.mark.parametrize("return_state", [True, False])
    async def test_async_task(self, mock_openai_credentials, return_state):
        @flow
        async def a_flow():
            return await task(self.async_fn)(1, return_state=return_state)

        result = await a_flow()
        if return_state:
            result = result.result()
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
