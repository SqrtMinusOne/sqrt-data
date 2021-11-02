FROM python:3.10-buster
# Install sqrt-data
WORKDIR "sqrt_data/"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sqrt_data/ setup.py ./
RUN pip install .
ENV PYTHONPATH="$PYTHONPATH:/sqrt_data"

# Copy the configuration and apply the crontab
WORKDIR "/"
COPY tasks.py ./

# Run mcron
CMD python tasks.py
