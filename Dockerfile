FROM quay.io/astronomer/astro-runtime:7.0.0

ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=true

USER root

# Set DBT root directory
ARG BASE_DIR="/usr/local/airflow/include/dbt"

# Grant access to the dbt project directory for everyone
RUN chmod -R 777 ${BASE_DIR}

# Create an alias for dbt commands so we don't have to activate every time
RUN printf '#!/bin/bash \n source /usr/local/airflow/dbt_venv/bin/activate && dbt $@' > /usr/bin/dbt
RUN chmod +x /usr/bin/dbt

USER astro
