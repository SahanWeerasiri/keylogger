# 4. Capture at the Kernel/Device Level to Survive Lock Screen

Date: 2026-10-20

## Status

Accepted

## Context

A key requirement was that recording continues during the lock screen. Lock screens are user-space graphical interfaces that intercept keyboard input before it reaches applications, but they do not block access to kernel input devices.

## Alternatives Considered

* **User-space hotkey daemons (sxhkd, desktop shortcuts)** — depend on the session; stop working at the lock screen.
* **evdev / eBPF capture** — independent of the display server and session state.

## Decision

We will capture at the kernel/device level (evdev device file or `input_event` kprobe). This is independent of Wayland/X11 and of whether the session is locked.

## Consequences

* **Positive:** Works during lock screen, across display servers, and regardless of focused window.
* **Negative:** Higher privilege requirements; the same property that makes it reliable also makes it indistinguishable from a malicious keylogger to security tooling.

