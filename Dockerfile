FROM mambaorg/micromamba:1.5.6
# Install sqrt-data
WORKDIR "/app/"
COPY environment.yml .
RUN micromamba env create -f environment.yml
COPY . .
ENV ENV_NAME=sqrt-data

RUN mkdir /tmp/sqrt-data
