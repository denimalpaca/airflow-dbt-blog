import os
from functools import partial
from include.utils import slack_callback_functions

if os.getenv("ENV", "DEV") == "sandbox":
    args = {
        "on_failure_callback": partial(
            slack_callback_functions.failure_callback,
            http_conn_id="slack_customer_success_de_feed"
        )
    }
else:
    args = {"depends_on_past": False}
