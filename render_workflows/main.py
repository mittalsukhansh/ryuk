"""Render registration entry point. Workflow environment must contain no payment secrets."""

from render import Retry, TaskContext, Workflows

from render_workflows.logic import verify_catalog

app = Workflows(
    default_retry=Retry(max_retries=0, wait_duration_ms=1000), default_timeout=30
)


@app.task(name="verify_catalog", timeout_seconds=30)
def verify_catalog_task(ctx: TaskContext, intent_data: dict) -> dict:
    """Read-only retries cannot dispatch payments; backend remains authoritative."""
    return verify_catalog(intent_data)


if __name__ == "__main__":
    app.start()
