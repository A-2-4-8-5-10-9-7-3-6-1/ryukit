<!-- ====================================================================== -->

# Setting Up
Before installing Poetry dependencies, configure environment variables:

```conf
POETRY_REPOSITORIES_DEVKIT_URL=https://link/to/python-devkit/repository
POETRY_HTTP_BASIC_DEVKIT_USERNAME=username
POETRY_HTTP_BASIC_DEVKIT_PASSWORD=gitub_pat
```

When using build task for distributables, it's necessary to add a file
**cmd/.env** with those same configurations.

<!-- ====================================================================== -->
