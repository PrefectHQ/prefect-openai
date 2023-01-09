import openai
from prefect_openai.credentials import OpenAICredentials


def test_openai_credentials_get_client():
    credentials = OpenAICredentials(token="token")
    client = credentials.get_client()
    assert client.api_key == "token"
