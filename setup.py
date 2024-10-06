"""Setup module"""

import codecs
import os.path
import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


def _read(rel_path):
    with codecs.open(os.path.join(here, rel_path), 'r') as file:
        return file.read()


def _get_version(rel_path):
    for line in _read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

    raise RuntimeError("Unable to find version string.")


setup(
    name="taswira",
    version=_get_version("src/taswira/__init__.py"),
    description="An interactive visualization tool for GCBM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moja-global/taswira",
    author="moja global",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires=">=3.6",
    install_requires=[
        "terracotta ==0.6.0",
        "dash ==1.13.3",
        "dash-leaflet ==0.0.19",
        "plotly ==4.8.2",
        "Werkzeug ==1.0.1",
        "tqdm ==4.47.0",
    ],
    extra_requires={
        'dev': ['pylint>=2.5.2', 'yapf>=0.30', 'isort>=4.3'],
        'test': ['pytest>=5.2']
    },
    entry_points={'console_scripts': [
        'taswira=taswira:main',
    ]},
)
