FROM continuumio/miniconda3:4.8.2 AS base
WORKDIR /taswira
COPY environment.yml .
RUN conda update conda \
      && conda install "conda=4.8.3" \
      && conda env create -f environment.yml \
      && conda clean -afy
ENV CONDA_ENV=/opt/conda/envs/taswira
ENV PATH="$CONDA_ENV/bin:$PATH"
COPY . .
RUN python -m pip install -e .

FROM base AS lint
RUN python -m pylint taswira

FROM base AS unit-test
RUN python -m pytest

ENTRYPOINT ["taswira"]
CMD ["--help"]
