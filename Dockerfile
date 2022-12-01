FROM quay.io/astronomer/astro-runtime:6.0.4

ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=true

USER root

# Set DBT root directory
ARG BASE_DIR="/usr/local/airflow/include/dbt"

# Create a venv for DBT and generate manifest.json files for each model
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-core==1.3.1 && \
    pip install --no-cache-dir dbt-postgres==1.3.1 && \
    dbt ls --profiles-dir ${BASE_DIR} --project-dir ${BASE_DIR}/jaffle_shop && \
    dbt deps --profiles-dir ${BASE_DIR} --project-dir ${BASE_DIR}/mrr-playbook && \
    dbt ls --profiles-dir ${BASE_DIR} --project-dir ${BASE_DIR}/mrr-playbook && deactivate

# Grant access to the dbt project directory for everyone
RUN chmod -R 777 ${BASE_DIR}

# Create an alias for dbt commands so we don't have to activate every time
RUN printf '#!/bin/bash \n source /usr/local/airflow/dbt_venv/bin/activate && dbt $@' > /usr/bin/dbt
RUN chmod +x /usr/bin/dbt

USER astro