import os

dbt_env_vars = {
    "DBT_USER": "{{ conn.snowflake_default.login }}",
    "DBT_ENV_SECRET_PASSWORD": "{{ conn.snowflake_default.password }}",
    "DBT_HOST": "{{ conn.snowflake_default.host }}",
    "DBT_SCHEMA": "{{ conn.snowflake_default.schema }}",
    "DBT_DATABASE": os.environ.get("DBT_DATABASE"),
    "DBT_WAREHOUSE": os.environ.get("DBT_WAREHOUSE"),
    "SNOWFLAKE_ACCOUNT": os.environ.get("SNOWFLAKE_ACCOUNT"),
    "SNOWFLAKE_USER": "{{ conn.snowflake_default.login }}",
    "SNOWFLAKE_PASSWORD": "{{ conn.snowflake_default.password }}",
    "ENV": "sandbox",
    "OPENLINEAGE_URL": os.environ.get("OPENLINEAGE_URL"),
    "OPENLINEAGE_API_KEY": os.environ.get("OPENLINEAGE_API_KEY"),
    "OPENLINEAGE_NAMESPACE": os.environ.get("OPENLINEAGE_NAMESPACE")
}
