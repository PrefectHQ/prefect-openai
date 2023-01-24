from unittest.mock import MagicMock

import pytest
from prefect import flow
from prefect.client.schemas import State
from prefect.utilities.asyncutils import is_async_fn

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


class TestInterpretException:
    def sync_fn(divisor: int):
        return 1 / divisor

    async def async_fn(divisor: int):
        return 1 / divisor

    @flow
    def sync_flow(divisor: int):
        return 1 / divisor

    @flow
    async def async_flow(divisor: int):
        return 1 / divisor

    @pytest.mark.parametrize("fn", [sync_fn, async_fn, sync_flow, async_flow])
    async def test_interpret_exception_no_error(self, mock_openai_credentials, fn):
        decorated_fn = interpret_exception("curie")(fn)
        if is_async_fn(fn):
            assert (await decorated_fn(1)) == 1
        else:
            assert decorated_fn(1) == 1
        assert mock_openai_credentials._mock_block_load.call_count == 0

    @pytest.mark.parametrize("fn", [sync_fn, sync_flow])
    def test_interpret_exception_error(self, mock_openai_credentials, fn):
        decorated_fn = interpret_exception("curie")(fn)
        with pytest.raises(ZeroDivisionError) as exc_info:
            decorated_fn(0)
        assert exc_info.value.args[0].startswith("[OpenAI Interpretation]")
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")

    @pytest.mark.parametrize("fn", [async_fn, async_flow])
    async def test_interpret_exception_error_async(self, mock_openai_credentials, fn):
        decorated_fn = interpret_exception("curie")(fn)
        with pytest.raises(ZeroDivisionError) as exc_info:
            await decorated_fn(0)
        assert exc_info.value.args[0].startswith("[OpenAI Interpretation]")
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")

    def test_interpret_exception_flow_return_state(self, mock_openai_credentials):
        decorated_fn = interpret_exception("curie")(self.sync_flow)
        result = decorated_fn(0, return_state=True)
        assert isinstance(result, State)
        assert result.message.startswith("[OpenAI Interpretation]")
        assert str(result.data) == result.message
        assert isinstance(result.data, ZeroDivisionError)
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")

    async def test_interpret_exception_flow_return_state_async(
        self, mock_openai_credentials
    ):
        decorated_fn = interpret_exception("curie")(self.async_flow)
        result = await decorated_fn(0, return_state=True)
        assert isinstance(result, State)
        assert result.message.startswith("[OpenAI Interpretation]")
        assert str(result.data) == result.message
        assert isinstance(result.data, ZeroDivisionError)
        mock_openai_credentials._mock_block_load.assert_called_once_with("curie")
