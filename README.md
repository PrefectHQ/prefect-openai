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

Retrieve the flow run name to create a story about it and an image using that story.

```python
from prefect import flow, get_run_logger
from prefect.context import get_run_context
from prefect_openai import OpenAICredentials, ImageModel, CompletionModel

@flow
def create_story_and_image_from_flow_run_name():
    logger = get_run_logger()
    context = get_run_context()
    flow_run_name = context.flow_run.name.replace("-", " ")

    credentials = OpenAICredentials.load("my-block")

    text_model = CompletionModel(openai_credentials=credentials, model="text-ada-001")
    text_prompt = f"Story about a {flow_run_name}"
    text_result = text_model.submit_prompt(text_prompt)

    image_prompt = text_result.choices[0].text.strip()
    image_model = ImageModel(openai_credentials=credentials)
    image_result = image_model.submit_prompt(image_prompt)
    image_url = image_result.data[0]["url"]

    logger.info(
        f"The story behind the image, {image_prompt!r}, "
        f"check it out here: {image_url}"
    )
    return image_url

create_image()
```

For example, a flow run named `space-orangutan` prompted a story about "A space orangutan is a species of monkey that live in and..." yielding this image:
![img-F2JuMSOh1c4rcLlKIVHfTI8B](https://user-images.githubusercontent.com/15331990/211466516-a40713b2-3730-4f77-8b01-b39308e36b97.png)

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
