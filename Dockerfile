FROM python:3.10-buster
# Install sqrt-data
WORKDIR "app/"
RUN pip install prefect
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN mkdir /tmp/sqrt-data
