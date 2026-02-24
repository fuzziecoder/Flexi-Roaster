"""Simple isolated worker process for Kubernetes worker pool deployments."""

from __future__ import annotations

import signal
import time

RUNNING = True


def _shutdown_handler(signum, frame):
    global RUNNING
    RUNNING = False


def main() -> None:
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    print("FlexiRoaster worker started. Waiting for tasks...")
    while RUNNING:
        # Placeholder for queue-based execution workers.
        # This keeps the worker pool isolated from API pods.
        print("worker-heartbeat")
        time.sleep(15)

    print("FlexiRoaster worker shutting down gracefully.")


if __name__ == "__main__":
    main()
