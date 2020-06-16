# Taswira

A CLI tool for visualizing GCBM output.

## Development Setup

First, obtain and install [Miniconda] if don't already have an Anaconda installation.

Next, create an environment with all the dependencies and then activate it:

```sh
$ conda env create -f environment.yml
$ conda activate taswira
```

Install, the CLI for development:

```sh
$ flit install -s
```

Now, you can run the tests:

```sh
$ pytest
```

Or, execute the CLI:

```sh
$ taswira
```

[miniconda]: https://docs.conda.io/en/latest/miniconda.html
