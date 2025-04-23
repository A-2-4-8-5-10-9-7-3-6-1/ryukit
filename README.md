<div align="center">
    <h1>RyuKit</h1>
    <p>A CLI management utiliy for Ryujinx on Windows platforms.</p>
</div>

## Installation

Use a Python package installer to download a package from the
[releases section](https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryukit/releases),
for example:

```sh
pipx install https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryukit/releases/download/v3.0.0/ryukit-3.0.0.tar.gz
```

You may then use it like:

```sh
python -m ryukit
```

or if the binary is in your PATH:

```sh
ryukit
```

## Development

There's a Dockerfile and docker-compose file for easy setup. Run the
`development` service through docker-compose to spin up a local development
environment. Additionally, there are settings and recommendations in the
`.vscode` folder; so VSCode is highly recommended for file editing. If using
VSCode as your editor, copy the contents from `.vscode/settings.public.json`
into `.vscode/settings.json` to correctly configure your editor.

## Licensing

Please read `LICENSE.md`.
