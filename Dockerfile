FROM apache/airflow:2.9.1

USER root
# Aqui está a mágica: instalamos 'libpq-dev' e 'gcc' para o Postgres não reclamar
RUN apt-get update && \
    apt-get install -y git libpq-dev gcc python3-dev && \
    apt-get clean

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt