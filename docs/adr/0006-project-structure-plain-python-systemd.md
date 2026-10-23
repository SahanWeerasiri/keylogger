# 7. Project Structure: Plain Python + systemd, No Custom eBPF Loader

Date: 2026-10-20

## Status

Accepted

## Context

The project is being wrapped up. We evaluated three viable capture paths and needed a final structure that is simple to ship, review, and operate, while preserving the eBPF exploration as documentation rather than runtime code.

## Alternatives Considered

* **Custom eBPF C program with libbpf loader** — most "kernel-native," but adds a build toolchain, ring-buffer consumer, and layout-mapping code.
* **Python + evdev + systemd** — minimal, readable, reliable.
* **auditd-only** — compliant but not a global recorder.

## Decision

The shipped project consists of:
* `/opt/keylog/keylog.py` — the evdev recorder.
* `/etc/systemd/system/keylog.service` — the supervising unit.
* `/var/log/keylog.log` — the append-only output.
* `docs/adr/` — this ADR set, including the eBPF exploration (ADR-0001) and the compliant audit alternative (ADR-0005) as documented options.

No custom eBPF loader is shipped. The bpftrace one-liner and the auditd configuration are documented as alternative operating modes.

## Consequences

* **Positive:** Small, auditable codebase; fast to deploy; easy to operate with standard systemd tooling; decision history preserved in ADRs.
* **Negative:** Character-level reconstruction is not built in; full "clipboard-like" semantics remain out of scope because the kernel cannot see selected text — a limitation established earlier in the discussion and accepted here.

