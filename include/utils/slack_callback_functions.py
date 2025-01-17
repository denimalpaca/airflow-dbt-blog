from airflow.hooks.base import BaseHook
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def failure_callback(context, **kwargs):
    slack_conn_id = kwargs["http_conn_id"]
    slack_webhook_token = BaseHook.get_connection(slack_conn_id).password
    log_url = context.get("task_instance").log_url
    slack_msg = f"""
            :x: Task has failed. 
            *Task*: {context.get('task_instance').task_id}
            *Dag*: {context.get('task_instance').dag_id} 
            *Execution Time*: {context.get('execution_date')}  
            <{log_url}| *Log URL*>
            """
    slack_alert = SlackWebhookOperator(
        task_id="slack_test",
        http_conn_id=slack_conn_id,
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username="airflow",
    )
    return slack_alert.execute(context=context)



