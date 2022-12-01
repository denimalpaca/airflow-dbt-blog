FROM quay.io/astronomer/astro-runtime:6.0.4

ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=true

USER root
COPY dbt-packages.txt ./
COPY dbt-requirements.txt ./
ARG BASE_DIR="/usr/local/airflow/include/dbt"
ARG JAFFLE_SHOP="/usr/local/airflow/include/dbt/jaffle_shop"
ARG MRR_PLAYBOOK="/usr/local/airflow/include/dbt/mrr-playbook"

RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    apt-get update && cat dbt-packages.txt | xargs apt-get install -y && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r dbt-requirements.txt && \
    dbt ls --profiles-dir ${BASE_DIR} --project-dir ${JAFFLE_SHOP} && \
    dbt deps --profiles-dir ${BASE_DIR} --project-dir ${MRR_PLAYBOOK} && \
    dbt ls --profiles-dir ${BASE_DIR} --project-dir ${MRR_PLAYBOOK} && deactivate

RUN chmod -R 777 ${BASE_DIR}

RUN printf '#!/bin/bash \n source /usr/local/airflow/dbt_venv/bin/activate && dbt $@' > /usr/bin/dbt
RUN chmod +x /usr/bin/dbt

USER astro