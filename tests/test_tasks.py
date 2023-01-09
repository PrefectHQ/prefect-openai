from prefect import flow

from prefect_openai.tasks import (
    goodbye_prefect_openai,
    hello_prefect_openai,
)


def test_hello_prefect_openai():
    @flow
    def test_flow():
        return hello_prefect_openai()

    result = test_flow()
    assert result == "Hello, prefect-openai!"


def goodbye_hello_prefect_openai():
    @flow
    def test_flow():
        return goodbye_prefect_openai()

    result = test_flow()
    assert result == "Goodbye, prefect-openai!"
