# `py-recall`

[![Release](https://img.shields.io/github/v/release/recallnet/py-recall)](https://img.shields.io/github/v/release/recallnet/py-recall)
[![Build status](https://img.shields.io/github/actions/workflow/status/recallnet/py-recall/main.yml?branch=main)](https://github.com/recallnet/py-recall/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/recallnet/py-recall/branch/main/graph/badge.svg)](https://codecov.io/gh/recallnet/py-recall)
[![Commit activity](https://img.shields.io/github/commit-activity/m/recallnet/py-recall)](https://img.shields.io/github/commit-activity/m/recallnet/py-recall)
[![License](https://img.shields.io/github/license/recallnet/py-recall)](https://img.shields.io/github/license/recallnet/py-recall)

> Python client for Recall Network storage & operations

> [!WARNING]
> This repository is a work in progress. It is not fully published yet nor is it ready for use.

## Table of Contents

- [Background](#background)
- [Usage](#usage)
- [Development](#development)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Install the dependencies](#2-install-the-dependencies)
  - [3. Set up the virtual environment](#3-set-up-the-virtual-environment)
  - [4. Run the pre-commit hooks](#4-run-the-pre-commit-hooks)
  - [5. Run the checks and tests](#5-run-the-checks-and-tests)
  - [6. Build the package](#6-build-the-package)
- [Contributing](#contributing)

## Background

This repository contains the Python client for Recall Network.

## Usage

This package is a work in progress.

## Development

### 1. Clone the repository

```bash
git clone git@github.com:recallnet/py-recall.git
```

### 2. Install the dependencies

```bash
make install
```

### 3. Set up the virtual environment

```bash
make install
```

### 4. Run the pre-commit hooks

Initially, the CI/CD pipeline might be failing due to formatting issues. To resolve those run:

```bash
uv run pre-commit run -a
```

This will also generate your `uv.lock` file

### 5. Run the checks and tests

```bash
make check
```

And run the tests with

```bash
make test
```

### 6. Build the package

```bash
make build
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.
