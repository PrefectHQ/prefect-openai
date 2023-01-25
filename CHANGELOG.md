# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## 0.1.1

Released on January 25th, 2022.

### Added

- `organization` field to the `OpenAICredentials` - [#8](https://github.com/PrefectHQ/prefect-openai/pull/8)
- `interpret_exception` decorator - [#11](https://github.com/PrefectHQ/prefect-openai/pull/11)
- `prompt_prefix` and `traceback_tail` keyword args to `interpret_exception` - [#14](https://github.com/PrefectHQ/prefect-openai/pull/14)

### Changed

- Made `model` to be a `Union[Literal, str]` - [#9](https://github.com/PrefectHQ/prefect-openai/pull/9)

## 0.1.0

Released on January 18th, 2022.

### Added

- `OpenAICredentials` and `CompletionModel` blocks - [#2](https://github.com/PrefectHQ/prefect-openai/pull/2)
- `ImageModel` block - [#3](https://github.com/PrefectHQ/prefect-openai/pull/3)
