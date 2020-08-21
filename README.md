# Taswira

> An interactive visualisation tool for GCBM.

![Continuous Integration](https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/workflows/Continuous%20Integration/badge.svg)

## Install

Requires [Git] and [Miniconda] (or Anaconda) with Python 3.6 or newer.

1. Clone the repository and `cd` into it:

```sh
git clone https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool.git

cd GSoC.FLINT.Visualisation_Tool
```

2. Create a conda environment and activate it:

```sh
conda env create -f environment.yml

conda activate taswira
```

3. Install the Python package:

```sh
pip install -e .
```

Taswira is now installed, see [Usage](#usage) below.

### Using Docker

You can also use Taswira through [Docker]. For that, build a container image:

```sh
DOCKER_BUILDKIT=1 docker build -t taswira:latest .
```

And then use it to run Taswira:

```sh
docker run taswira
```

[Miniconda]: https://docs.conda.io/en/latest/miniconda.html
[Git]: https://git-scm.com/
[Docker]: https://docs.docker.com/get-docker/

## Usage

```
usage: taswira [-h] [--allow-unoptimized] config spatial_results db_results

Interactive visualization tool for GCBM

positional arguments:
  config               path to JSON config file
  spatial_results      path to GCBM spatial output directory
  db_results           path to compiled GCBM results database

optional arguments:
  -h, --help           show this help message and exit
  --allow-unoptimized  allow processing unoptimized raster files
```

## Repository Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://moja.global"><img src="https://avatars1.githubusercontent.com/u/19564969?v=4" width="100px;" alt=""/><br /><sub><b>moja global</b></sub></a><br /><a href="#projectManagement-moja-global" title="Project Management">📆</a></td>
    <td align="center"><a href="https://abhineet.tk"><img src="https://avatars1.githubusercontent.com/u/11965776?v=4" width="100px;" alt=""/><br /><sub><b>Abhineet Tamrakar</b></sub></a><br /><a href="https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/commits?author=abhineet97" title="Documentation">📖</a> <a href="https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/commits?author=abhineet97" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/kaskou"><img src="https://avatars1.githubusercontent.com/u/8544371?v=4" width="100px;" alt=""/><br /><sub><b>kaushik surya sangem</b></sub></a><br /><a href="https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/pulls?q=is%3Apr+reviewed-by%3Akaskou" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/gmajan"><img src="https://avatars0.githubusercontent.com/u/8733319?v=4" width="100px;" alt=""/><br /><sub><b>Guy Janssen</b></sub></a><br /><a href="#projectManagement-gmajan" title="Project Management">📆</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind are welcome!

## Maintainers Reviewers Ambassadors Coaches

The following people are Maintainers Reviewers Ambassadors or Coaches
<table><tr>

<td align="center"><a href="https://abhineet.tk"><img src="https://avatars1.githubusercontent.com/u/11965776?v=4" width="100px;" alt=""/><br /><sub><b>Abhineet Tamrakar</b></sub></a><br /><a href="https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/commits?author=abhineet97" title="Documentation">📖</a> <a href="https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/commits?author=abhineet97" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/kaskou"><img src="https://avatars1.githubusercontent.com/u/8544371?v=4" width="100px;" alt=""/><br /><sub><b>kaushik surya sangem</b></sub></a><br /><a href="https://github.com/moja-global/GSoC.FLINT.Visualisation_Tool/pulls?q=is%3Apr+reviewed-by%3Akaskou" title="Reviewed Pull Requests">👀</a></td>
</tr>
</table>

**Maintainers** review and accept proposed changes\
**Reviewers** check proposed changes before they go to the Maintainers\
**Ambassadors** are available to provide training related to this repository\
**Coaches** are available to provide information to new contributors to this repository
