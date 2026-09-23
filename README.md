# Python Agentscript Demo

This repository demonstrates protecting Python functions with Agentscript.

## Local verification

From the repository root:

```text
crane check
```

The GitHub Actions workflow runs the same policy check on every push and pull
request.

The checkpoint under `.crane/checkpoints` is metadata-only: Crane reads the
baseline functions from the recorded local Git commit and the current
functions from the worktree. No copied target snapshots are required.
