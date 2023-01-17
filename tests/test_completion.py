from unittest.mock import MagicMock

from prefect_openai.completion import CompletionModel


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
