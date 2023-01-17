from prefect_openai.credentials import OpenAICredentials


def test_openai_credentials_get_client():
    credentials = OpenAICredentials(api_key="api_key")
    assert credentials.api_key.get_secret_value() == "api_key"

    client = credentials.get_client()
    assert client.api_key == "api_key"
