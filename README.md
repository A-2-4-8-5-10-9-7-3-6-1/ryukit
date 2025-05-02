<div align="center">
    <h1>RyuKit</h1>
    <p>A CLI management utiliy for Ryujinx on Windows platforms.</p>
</div>

## Installation

Download an executable from the
[releases section](https://github.com/A-2-4-8-5-10-9-7-3-6-1/ryukit/releases).
Once installed, assuming you have the executable in your PATH variable, use it
like:

```sh
ryukit
```

In particular, this command will display the help information.

## Development

There's a Dockerfile and docker-compose file for easy setup. Run the
`development` service through docker-compose to spin up a local development
environment. Additionally, there are settings and recommendations in the
`.vscode` folder; so VSCode is highly recommended for file editing. If using
VSCode as your editor, copy the contents from `.vscode/settings.public.json`
into `.vscode/settings.json` to correctly configure your editor.

On building the development container, wine might prompt you to install some
dependencies, please accept the installation.

## Licensing

Please read `LICENSE.md`.

## Acknowledgements

- Image `resources/exe.ico` by
  [Alfredo Hernandez](https://www.alfredocreates.com).
