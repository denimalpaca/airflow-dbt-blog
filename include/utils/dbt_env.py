dbt_env_vars = {
    "DBT_USER": "{{ conn.postgres.login }}",
    "DBT_ENV_SECRET_PASSWORD": "{{ conn.postgres.password }}",
    "DBT_HOST": "{{ conn.postgres.host }}",
    "DBT_SCHEMA": "{{ conn.postgres.schema }}",
    "DBT_PORT": "{{ conn.postgres.port }}",
}

dbt_cmd = "source /usr/local/airflow/dbt_venv/bin/activate && dbt"