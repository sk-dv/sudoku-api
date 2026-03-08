import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("FLASK_ENV", "production"),
        traces_sample_rate=0.1,
        integrations=[
            # Captura logger.exception() como errores en Sentry
            LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
        ],
    )
