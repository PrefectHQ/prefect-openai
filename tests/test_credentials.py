from prefect_openai.credentials import OpenAICredentials


def test_openai_credentials_get_client():
    credentials = OpenAICredentials(api_key="api_key", organization="my_org")
    assert credentials.api_key.get_secret_value() == "api_key"
    assert credentials.organization == "my_org"

    client = credentials.get_client()
    assert client.api_key == "api_key"
    assert client.organization == "my_org"
