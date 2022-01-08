FROM python:3.10-buster
# Install sqrt-data
WORKDIR "sqrt_data/"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sqrt_data/ setup.py ./
RUN pip install .
ENV PYTHONPATH="$PYTHONPATH:/sqrt_data"

WORKDIR "/"
RUN mkdir /tmp/sqrt-data

CMD sqrt_data cron run-server-cron
