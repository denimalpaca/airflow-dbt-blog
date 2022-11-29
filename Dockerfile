FROM quay.io/astronomer/astro-runtime:6.0.4

ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=true

USER root
COPY dbt-packages.txt ./
COPY dbt-requirements.txt ./
ARG DBT_DIR="/usr/local/airflow/include/dbt"

RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    apt-get update && cat dbt-packages.txt | xargs apt-get install -y && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r dbt-requirements.txt && \
    dbt ls --profiles-dir ${DBT_DIR} --project-dir ${DBT_DIR} && deactivate

RUN chmod -R 777 ${DBT_DIR}

USER astro