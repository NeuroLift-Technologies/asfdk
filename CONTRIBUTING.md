# Contributing to NeuroLift Technologies Projects

Thank you for your interest in contributing! These guidelines apply to all repositories in the **NeuroLift Technologies** organization unless a repository provides its own `CONTRIBUTING.md`.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Pull Request Process](#pull-request-process)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

By participating in any of our projects, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## How to Contribute

1. **Fork** the repository you want to contribute to.
2. **Create a branch** from `main` for your change:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**, following the style guidelines below.
4. **Write or update tests** to cover your change.
5. **Open a pull request** targeting the `main` branch, filling in the PR template.

## Reporting Bugs

Use the **Bug Report** issue template. Before filing, please:

- Search existing issues to avoid duplicates.
- Describe the bug clearly: expected vs. actual behavior.
- Include steps to reproduce and your environment details.

## Suggesting Features

Use the **Feature Request** issue template. Please:

- Clearly describe the problem you're trying to solve.
- Explain why this feature would benefit others.
- Provide examples or mockups if possible.

## Pull Request Process

The [ORG-DEV-OTOI-1.0.4 organization contract](https://github.com/NeuroLift-Technologies/.github/blob/main/governance.yaml)
sets the required minimum. Use the [agent contribution template](PULL_REQUEST_TEMPLATE/agent-contribution.md)
and follow [REVIEW.md](REVIEW.md) for agent reviews.

1. Ensure all existing tests pass and add new tests for new behavior.
2. Update documentation if your change affects the public API or user-facing behavior.
3. Keep pull requests focused — one change per PR.
4. A maintainer will review your PR. Address any requested changes promptly.
5. Once approved and all checks pass, a maintainer will merge your PR.

## Development Setup

Each repository has its own setup instructions in its own `README.md`. Refer to those for repository-specific bootstrapping steps.

## Style Guidelines

- Follow the language-specific conventions already used in each repository.
- Write clear, descriptive commit messages (prefer the imperative mood: "Add feature" not "Added feature").
- Comment non-obvious logic; let simple code speak for itself.
