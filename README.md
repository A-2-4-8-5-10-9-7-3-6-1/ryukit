# RyujinxKit

RyujinxKit is a Python package designed to facilitate the management of a Windows Ryujinx distribution.
It provides tools for handling save data, configuring settings, and automating common tasks related to Ryujinx.

## Features

- Install a Ryujinx distribution.
- Manage save data (create, delete, export, ...).
- Retrieve system and application information.

## Installation

RyujinxKit is distributed as a Python package and can be installed using [Poetry](https://python-poetry.org/) or `pip`.

```sh
pip install ryujinxkit
```

Alternatively, install from source:

```sh
git clone https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryujinxkit.git
cd ryujinxkit
poetry install
```

## Usage

### CLI Commands

RyujinxKit provides a command-line interface for easy management.

```sh
ryujinxkit --help
```

#### Example Commands

- Install Ryujinx:
  ```sh
  ryujinxkit
  ```
- List save data:
  ```sh
  ryujinxkit save
  ```

## Development

### Running Tests

This project uses `pytest` for testing. To run tests, execute:

```sh
pytest
```

### Linting and Formatting

Code formatting is enforced using `black`, `isort`, `prettier`, and `pyright`.

### Development Environment

A development container service (`development`) is included in `docker-compose.yaml`,
which automates environment setup (installing dependencies like Poetry, Git, Hadolint, etc.).

### Recommended Editor

It is recommended to use **VSCode** for development, as the repository contains configuration files
optimized for it.

## License

This project is licensed under the terms specified in `LICENSE.md`.

## Contributing

Contributions are welcome! Please check `TODO.md` for planned features and improvements.
