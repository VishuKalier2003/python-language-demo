# Python Agentscript Demo

This repository demonstrates protecting Python functions with Agentscript.

## Repository contract

The application repository owns its policies and trusted checkpoint:

- `.crane/policies/` contains the reviewed preserve rules.
- `.crane/checkpoints/baseline.json` identifies the trusted application Git
  commit.
- The Crane executable is not committed to this repository.

The checkpoint belongs to this Python repository, not to the Crane repository.
Crane is the independent verifier that reads the checkpoint commit and current
worktree.

## Local verification

Install or download Crane v0.1.2, then from this repository root:

```bash
crane --version
crane status
crane context
crane check --json
```

The expected result is:

```json
{"status": "passed", "violations": []}
```

To test a violation, change `PaymentService.charge` or `calculate_tax` in
`payment.py` and run:

```bash
crane check --agent
```

The command returns a non-zero exit code and structured violation JSON. Restore
the function to its checkpoint version and run the command again to pass.
Formatting-only and comment-only changes are ignored by the canonical code
comparison; code-token changes fail.

## GitHub Actions verification

[`agentscript.yml`](./.github/workflows/agentscript.yml) checks out the full
application history, downloads the pinned Crane v0.1.2 Linux release, verifies
its SHA-256 digest, prints the active context, and runs:

```text
crane check --json
```

The workflow does not clone Crane source or install Rust. A failed check exits
non-zero and fails the pull request or push workflow.

The release version is intentionally pinned. Upgrade it only through a
reviewed change to `CRANE_VERSION` and `CRANE_SHA256` after a new Crane release
has passed compatibility testing.

## Agent adapter lifecycle

An external adapter such as a Claude Code, Codex, or Copilot host remains the
orchestrator; it does not duplicate policy semantics:

```text
adapter: crane context
  -> send context to agent
  -> agent edits payment.py
  -> adapter: crane check --agent
  -> send violations back to agent
  -> agent repairs
  -> adapter: crane check --agent
  -> exit 0 means the local contract passes
  -> GitHub Actions independently runs crane check --json
```

Crane also exposes the explicit adapter contract:

```bash
crane agent init --profile claude
crane agent verify --profile claude
```

`agent init` initializes and immediately verifies the repository. `agent verify`
returns the stable JSON result and a non-zero exit status when repair is
required. These commands never move checkpoints or modify application source.
