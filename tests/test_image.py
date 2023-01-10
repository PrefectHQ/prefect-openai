from unittest.mock import MagicMock

from prefect_openai.image import ImageModel


def test_image_model_create(mock_openai_credentials: MagicMock):
    image_model = ImageModel(
        openai_credentials=mock_openai_credentials,
    )
    prompt = "what is meaning of meaning"
    image_model.submit_prompt(prompt)
    mock_openai_credentials._mock_model.acreate.assert_called_once_with(
        prompt="what is meaning of meaning", size="256x256", n=1, response_format="url"
    )


def test_image_model_create_override(mock_openai_credentials: MagicMock):
    image_model = ImageModel(
        openai_credentials=mock_openai_credentials,
    )
    prompt = "what is meaning of meaning"
    image_model.submit_prompt(prompt, size="512x512", n=8)
    mock_openai_credentials._mock_model.acreate.assert_called_once_with(
        prompt="what is meaning of meaning", size="512x512", n=8, response_format="url"
    )
