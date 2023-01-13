FROM quay.io/astronomer/astro-runtime:7.1.0

ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=true

USER root

# Set DBT root directory
ARG DBT_DIR_DEFAULT="/usr/local/airflow/include/dbt"
ENV DBT_DIR=$DBT_DIR_DEFAULT
ENV DBT_PROFILES_DIR=$DBT_DIR_DEFAULT

RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir openlineage-dbt==0.17.0 dbt-core==1.3.0 dbt-snowflake==1.3.0

# Create an alias for dbt commands so we don't have to activate every time
RUN echo -e '#!/bin/bash' > /usr/bin/dbt && \
    echo -e "source /usr/local/airflow/dbt_venv/bin/activate && dbt \$@" >> /usr/bin/dbt

# Grant access to the dbt project directory for everyone
RUN chmod -R 777 ${DBT_DIR}
RUN chmod -R 777 /usr/bin/dbt

# Fivetran extractor isn't operational yet, so we use the local versions of the packages
RUN cp -r /usr/local/airflow/include/fivetran_provider /usr/local/lib/python3.9/site-packages/ && \
    cp -r /usr/local/airflow/include/airflow_provider_fivetran-1.1.3.dist-info /usr/local/lib/python3.9/site-packages/ && \
    cp -r /usr/local/airflow/include/fivetran_provider_async /usr/local/lib/python3.9/site-packages/ && \
    cp -r /usr/local/airflow/include/airflow_provider_fivetran_async-1.0.0a4.dist-info /usr/local/lib/python3.9/site-packages/ && \
    cp -r /usr/local/airflow/include/cosmos /usr/local/lib/python3.9/site-packages/ && \
    cp -r /usr/local/airflow/include/astronomer_cosmos-0.2.0.dist-info /usr/local/lib/python3.9/site-packages/

USER astro
