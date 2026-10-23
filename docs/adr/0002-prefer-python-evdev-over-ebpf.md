# 2. Prefer Python + evdev over eBPF for the Usable Recorder

Date: 2026-10-20

## Status

Accepted

## Context

The eBPF path proved technically workable but inconvenient: scancodes need layout mapping, and building a full user-space loader adds complexity. We needed a simple recorder that "just works."

## Alternatives Considered

* **eBPF/bpftrace** — kernel-level, raw scancodes, more moving parts.
* **Python + evdev** — reads `/dev/input/by-path/...-event-kbd`, returns key names like `KEY_A`, handles the event struct for us.
* **auditd** — compliant but limited to TTY input.

## Decision

We will implement the usable recorder in Python using the `evdev` library, reading directly from the keyboard device:

```python
import evdev
from evdev import ecodes

DEV = '/dev/input/by-path/platform-i8042-serio-0-event-kbd'

dev = evdev.InputDevice(DEV)
with open('/var/log/keylog.log', 'a') as f:
    for ev in dev.read_loop():
        if ev.type == ecodes.EV_KEY:
            k = evdev.categorize(ev)
            if k.keystate == k.key_down:
                f.write(f"{ev.timestamp()} {k.keycode}\n")
                f.flush()
```

Requires membership in the `input` group or root.

## Consequences

* **Positive:** Minimal code, readable key names, easy to run and debug, no kernel code.
* **Negative:** Requires `input` group/root; still a keylogger pattern from a security-monitoring perspective; does not produce an audit-grade trail.

