"""Explicit operator-only Render trigger with public fixture data, never buyer information."""

import argparse
import json
import os
from pathlib import Path

from render import Render


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task_slug", help="Copy workflow-slug/verify_catalog from Render Dashboard"
    )
    args = parser.parse_args()
    if not os.environ.get("RENDER_API_KEY"):
        parser.error(
            "Set RENDER_API_KEY privately; never pass credentials as command arguments"
        )
    if not args.task_slug.endswith("/verify_catalog") or len(args.task_slug) > 200:
        parser.error("Expected workflow-slug/verify_catalog")
    payload = json.loads(Path(__file__).with_name("demo-input.json").read_text())
    try:
        task = Render().workflows.start_task(args.task_slug, [payload])
        print(
            json.dumps(
                {
                    "run_id": task.id,
                    "note": "Inspect this run in Render; no checkout created",
                }
            )
        )
    except Exception:
        parser.exit(
            1, "Render trigger unavailable. Inspect existing runs before retrying.\n"
        )


if __name__ == "__main__":
    main()
