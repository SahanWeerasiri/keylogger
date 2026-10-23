# 6. Store Output as Timestamped Scancode/Keycode Logs

Date: 2026-10-20

## Status

Accepted

## Context

Captured events need a durable, simple format that supports later reconstruction and forensic review, while keeping the recorder minimal.

## Alternatives Considered

* **Binary event dumps** — compact but opaque and harder to review.
* **Plain-text timestamped lines** — simple, greppable, append-only.
* **Database** — heavier, unnecessary for a simple recorder.

## Decision

We will write append-only plain-text lines of the form:

```
<timestamp> <keycode>
```

flushing after each write, to `/var/log/keylog.log` (evdev path) or `/var/log/keylog-bpf.log` (eBPF path). Character reconstruction from layout is left to post-processing.

## Consequences

* **Positive:** Simple, greppable, append-only, easy to archive; flush ensures data is not lost on crash.
* **Negative:** Log grows unbounded without rotation; character reconstruction depends on the keyboard layout at capture time, which must be recorded or known separately.

