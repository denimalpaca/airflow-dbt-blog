drop table if exists {{ params.schema_name }}.{{ params.table_name }};
create table {{ params.schema_name }}.{{ params.table_name }} (
  id int,
  user_id int,
  order_date date,
  status varchar
);
copy into {{ params.schema_name }}.{{ params.table_name }}
  from 'gcs://{{ var.value.gcs_bucket }}/dbt-core-demo/{{ params.table_name }}.csv'
  storage_integration = CS_GCS_INT
  file_format = (type = csv, skip_header = 1)
;