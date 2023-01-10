# prefect-openai

Visit the full docs [here](https://PrefectHQ.github.io/prefect-openai) to see additional examples and the API reference.

<p align="center">
    <a href="https://pypi.python.org/pypi/prefect-openai/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect-openai?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/PrefectHQ/prefect-openai/" alt="Stars">
        <img src="https://img.shields.io/github/stars/PrefectHQ/prefect-openai?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/prefect-openai/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/prefect-openai?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/PrefectHQ/prefect-openai/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/PrefectHQ/prefect-openai?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect-community.slack.com" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.prefect.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
</p>

## Welcome!

Prefect integrations for working with OpenAI.

## Getting Started

### Python setup

Requires an installation of Python 3.7+.

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Prefect 2.0. For more information about how to use Prefect, please refer to the [Prefect documentation](https://orion-docs.prefect.io/).

### Installation

Install `prefect-openai` with `pip`:

```bash
pip install prefect-openai
```

A list of available blocks in `prefect-openai` and their setup instructions can be found [here](https://PrefectHQ.github.io/prefect-openai/#blocks-catalog).

### Write and run a flow

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

For more tips on how to use tasks and flows in a Collection, check out [Using Collections](https://orion-docs.prefect.io/collections/usage/)!

## Resources

If you encounter any bugs while using `prefect-openai`, feel free to open an issue in the [prefect-openai](https://github.com/PrefectHQ/prefect-openai) repository.

If you have any questions or issues while using `prefect-openai`, you can find help in either the [Prefect Discourse forum](https://discourse.prefect.io/) or the [Prefect Slack community](https://prefect.io/slack).

Feel free to star or watch [`prefect-openai`](https://github.com/PrefectHQ/prefect-openai) for updates too!

## Contributing

If you'd like to help contribute to fix an issue or add a feature to `prefect-openai`, please [propose changes through a pull request from a fork of the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

Here are the steps:

1. [Fork the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
2. [Clone the forked repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
3. Install the repository and its dependencies:
```
pip install -e ".[dev]"
```
4. Make desired changes
5. Add tests
6. Insert an entry to [CHANGELOG.md](https://github.com/PrefectHQ/prefect-openai/blob/main/CHANGELOG.md)
7. Install `pre-commit` to perform quality checks prior to commit:
```
pre-commit install
```
8. `git commit`, `git push`, and create a pull request
