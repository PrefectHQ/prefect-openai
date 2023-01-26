# Coordinate and use AI in your dataflow with `prefect-openai`

<p align="center">
    <img src="https://user-images.githubusercontent.com/15331990/213825004-eedb25b3-0520-4f55-95d3-3a3fc8b235ff.png">
    <br>
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

Visit the full docs [here](https://PrefectHQ.github.io/prefect-openai) to see additional examples and the API reference.

The `prefect-openai` collection makes it easy to leverage the capabilities of AI in your flows. Check out the examples below to get started!

## Getting Started

### Summarize tracebacks with GPT3

Tracebacks--it's quintessential in programming. They are a record of every line of code leading to the error, to help us, humans, determine what's wrong with the program and find a solution.

However, tracebacks can be extraordinarily complex, especially for someone new to the codebase.

To streamline this process, we could add AI to the mix, to offer a more human-readable summary of the issue, so it's easier for the developer to understand what went wrong and implement a fix.

After installing `prefect-openai` and [saving an OpenAI key](#saving-an-openai-key), you can easily incorporate OpenAI within your flows to help you achieve the aforementioned benefits!

```python
from prefect import flow, get_run_logger
from prefect_openai import OpenAICredentials, CompletionModel


@flow
def summarize_traceback(traceback: str) -> str:
    logger = get_run_logger()
    openai_credentials = OpenAICredentials.load("openai-credentials")
    completion_model = CompletionModel(
        openai_credentials=openai_credentials,
        model="text-curie-001",
        max_tokens=512,
    )
    prompt = f"Summarize cause of error from this traceback: ```{traceback}```"
    summary = completion_model.submit_prompt(traceback).choices[0]["text"]
    logger.info(f"Summary of the traceback: {summary}")
    return summary


if __name__ == "__main__":
    traceback = """
        ParameterBindError: Error binding parameters for function 'summarize_traceback': missing a required argument: 'traceback'.
        Function 'summarize_traceback' has signature 'traceback: str) -> str' but received args: () and kwargs: {}.
    """
    summarize_traceback(traceback)
```

```bash hl_lines="4"
...
12:29:32.085 | INFO    | Flow run 'analytic-starling' - Finished text completion using the 'text-curie-001' model with 113 tokens, creating 1 choice(s).
12:29:32.089 | INFO    | Flow run 'analytic-starling' - Summary of the traceback:     
This error is caused by the missing argument traceback. The function expects a traceback object as its first argument, but received nothing.
...
```
Notice how the original traceback was quite long and confusing.

On the flip side, the Curie GPT3 model was able to summarize the issue eloquently!

!!! info "Built-in decorator"

    No need to build this yourself, `prefect-openai` features a
    [built-in decorator](completion/#prefect_openai.completion.interpret_exception)
    to help you automatically catch and interpret exceptions in flows, tasks, and even
    vanilla Python functions.

    ```python
    import httpx
    from prefect_openai.completion import interpret_exception

    @interpret_exception("COMPLETION_MODEL_BLOCK_NAME_PLACEHOLDER")
    def example_func():
        resp = httpx.get("https://httpbin.org/status/403")
        resp.raise_for_status()

    example_func()
    ```

### Create a story around a flow run name with GPT3 and DALL-E

Have you marveled at all the AI-generated images and wondered how others did it?

After installing `prefect-openai` and [saving an OpenAI key](#saving-an-openai-key), you, too, can create AI-generated art.

Here's an example on how to create a story and an image based off a flow run name.

```python
from prefect import flow, task, get_run_logger
from prefect.context import get_run_context
from prefect_openai import OpenAICredentials, ImageModel, CompletionModel


@task
def create_story_from_name(credentials: OpenAICredentials, flow_run_name: str) -> str:
    """
    Create a fun story about the flow run name.
    """
    text_model = CompletionModel(
        openai_credentials=credentials, model="text-curie-001", max_tokens=288
    )
    text_prompt = f"Provide a fun story about a {flow_run_name}"
    story = text_model.submit_prompt(text_prompt).choices[0].text.strip()
    return story


@task
def create_image_from_story(credentials: OpenAICredentials, story: str) -> str:
    """
    Create an image associated with the story.
    """
    image_model = ImageModel(openai_credentials=credentials, size="512x512")
    image_result = image_model.submit_prompt(story)
    image_url = image_result.data[0]["url"]
    return image_url


@flow
def create_story_and_image_from_flow_run_name() -> str:
    """
    Get the flow run name and create a story and image associated with it.
    """
    context = get_run_context()
    flow_run_name = context.flow_run.name.replace("-", " ")

    credentials = OpenAICredentials.load("openai-credentials")
    story = create_story_from_name(credentials=credentials, flow_run_name=flow_run_name)
    image_url = create_image_from_story(credentials=credentials, story=story)

    story_and_image = (
        f"The story about a {flow_run_name}: '{story}' "
        f"And its image: {image_url}"
    )
    print(story_and_image)
    return story_and_image


create_story_and_image_from_flow_run_name()
```

### Saving an OpenAI key

It's easy to set up an `OpenAICredentials` block!

1. Head over to https://beta.openai.com/account/api-keys
2. Login to your OpenAI account
3. Click "+ Create new secret key"
4. Copy the generated API key
5. Create a short script, replacing the placeholders (or do so in the UI)

```python
from prefect_openai import OpenAICredentials`
OpenAICredentials(api_key="API_KEY_PLACEHOLDER").save("BLOCK_NAME_PLACEHOLDER")
```

Congrats! You can now easily load the saved block, which holds your OpenAI API key:

```python
from prefect_openai import OpenAICredentials
OpenAICredentials.load("BLOCK_NAME_PLACEHOLDER")
```

Visit [Flow Run Name Art](flow_run_name_art) to see some example output!

## Resources

For more tips on how to use tasks and flows in a Collection, check out [Using Collections](https://orion-docs.prefect.io/collections/usage/)!

### Installation

Install `prefect-openai` with `pip`:

```bash
pip install prefect-openai
```

Requires an installation of Python 3.7+.

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Prefect 2.0. For more information about how to use Prefect, please refer to the [Prefect documentation](https://orion-docs.prefect.io/).

### Feedback

If you encounter any bugs while using `prefect-openai`, feel free to open an issue in the [prefect-openai](https://github.com/PrefectHQ/prefect-openai) repository.

If you have any questions or issues while using `prefect-openai`, you can find help in either the [Prefect Discourse forum](https://discourse.prefect.io/) or the [Prefect Slack community](https://prefect.io/slack).

Feel free to star or watch [`prefect-openai`](https://github.com/PrefectHQ/prefect-openai) for updates too!

### Contributing

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
