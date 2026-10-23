# 1. Use eBPF/bpftrace for Kernel-Level Keystroke Capture

Date: 2026-10-20

## Status

Accepted (as an exploration/learning path, not the primary runtime)

## Context

We wanted to know whether eBPF could be used to build a keylogger or clipboard-like tool, and what differences exist versus user-space approaches. The Linux input subsystem delivers raw hardware events through the kernel function `input_event`, and eBPF can attach a kprobe there.

## Alternatives Considered

* **Python + evdev** — reads `/dev/input/eventX` from user space; simpler, yields key names.
* **auditd + pam_tty_audit** — native TTY audit; compliant but not a global keylogger.
* **eBPF kprobe on `input_event`** — kernel-level capture, raw scancodes only.

## Decision

We will use a `bpftrace` kprobe on `input_event`, filtered to `EV_KEY` and key-down state, as the eBPF exploration path:

```bash
sudo bpftrace -e 'kprobe:input_event /arg1 == 1 && arg3 == 1/ { printf("%llu %d\n", nsecs, arg2); }'
```

We accept that this yields scancodes, not characters, and that layout mapping must happen elsewhere.

## Consequences

* **Positive:** Direct visibility into kernel input handling; minimal code; useful for learning eBPF.
* **Negative:** Raw scancodes require user-space layout mapping; requires root/`CAP_BPF`; no built-in audit trail; kernel-level keylogging is a known MITRE ATT&CK technique (T1056.001) and may be flagged by EDR.

