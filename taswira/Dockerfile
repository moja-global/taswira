FROM continuumio/miniconda3:4.8.2 AS base
WORKDIR /taswira
RUN conda update conda && conda install "conda=4.8.3"
COPY environment.yml .
RUN conda env create -f environment.yml
ENV CONDA_ENV=/opt/conda/envs/taswira
ENV PATH="$CONDA_ENV/bin:$PATH"
COPY . .
RUN FLIT_ROOT_INSTALL=1 python -m flit install -s

FROM base AS lint
RUN python -m pylint taswira

FROM base AS unit-test
RUN python -m pytest

ENTRYPOINT ["taswira"]
CMD ["--help"]
