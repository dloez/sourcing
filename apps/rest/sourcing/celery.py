from celery import Celery

from sourcing.config import REDIS_URL
from sourcing.source.aspsp.tasks.get_account_balances import (
    wrap_spawn_users_balance_collectors,
)

app = Celery(
    "sourcing",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

app.conf.update(timezone="UTC", broker_connection_retry_on_startup=True)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    # sender.add_periodic_task(10, wrap_get_store_aspsps.s())
    # sender.add_periodic_task(60 * 30, wrap_spawn_users_balance_collectors.s())
    sender.add_periodic_task(30, wrap_spawn_users_balance_collectors.s())
