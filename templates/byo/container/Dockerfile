FROM python:3.9-slim-buster

ARG model_files_dir

# Install OS pacakges
RUN apt-get -y update  \
    && apt-get install -y --no-install-recommends nginx  \
    && rm -rf /var/lib/apt/lists/*

# Set Python environment variables - https://docs.python.org/3/using/cmdline.html#environment-variables
# PYTHONUNBUFFERED keeps Python from buffering standard output stream so logs can be delivered to the user quickly
# PYTHONDONTWRITEBYTECODE keeps Python from writing the .pyc files which are unnecessary in this case
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# Setup virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /opt/program
ENV PATH="/opt/program:${PATH}"

# Setup serving wrapper
COPY "config" ./config
COPY "serving" .
RUN pip install --no-cache-dir gunicorn

# Setup permissions for Serverless endpoint - https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints-troubleshooting.html
RUN chmod o+rwX -R /opt/program

# Setup inference app
COPY "$model_files_dir" .
RUN pip install --no-cache-dir -r requirements.txt

# Add an entrypoint
ENTRYPOINT ["python", "serve.py"]