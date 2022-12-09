import os

dbt_env_vars = {
    "DBT_USER": "{{ conn.snowflake_default.login }}",
    "DBT_ENV_SECRET_PASSWORD": "{{ conn.snowflake_default.password }}",
    "DBT_HOST": "{{ conn.snowflake_default.host }}",
    "DBT_SCHEMA": "{{ conn.snowflake_default.schema }}",
    "OPENLINEAGE_URL": "https://benjisandbox.datakin.com",
    "OPENLINEAGE_API_KEY": os.env.get("OPENLINEAGE_API_KEY"),
    "SNOWFLAKE_ACCOUNT": os.env.get("SNOWFLAKE_ACCOUNT"),
    "SNOWFLAKE_USER": "{{ conn.snowflake_default.login }}",
    "SNOWFLAKE_PASSWORD": "{{ conn.snowflake_default.password }}",
    "ENV": "sandbox"
}
