FROM continuumio/miniconda3:4.8.2-alpine

WORKDIR /taswira

ENV CONDA_ROOT=/opt/conda
ENV PATH="$CONDA_ROOT/bin:$PATH"
COPY environment.yml /taswira
RUN conda env create -f environment.yml
