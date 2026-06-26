# pyutils

![PyPI version](https://img.shields.io/pypi/v/pyutils.svg)

Python Boilerplate contains all the boilerplate you need to create a Python package.): Collection of interesting utilities accumulated over the years (most of them aren't mine and will be trie

* [GitHub](https://github.com/baskettaz/pyutils/) | [PyPI](https://pypi.org/project/pyutils/) | [Documentation](https://baskettaz.github.io/pyutils/)
* Created by [Vesselin Tsvetanov](-) | GitHub [@baskettaz](https://github.com/baskettaz) | PyPI [@d credit to be given)](https://pypi.org/user/d credit to be given)/)
* MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://baskettaz.github.io/pyutils/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/pyutils.git
cd pyutils

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `pyutils`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

pyutils was created in 2026 by Vesselin Tsvetanov.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
