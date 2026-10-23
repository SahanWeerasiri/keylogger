# 3. Use systemd for Background Operation and Auto-Restart

Date: 2026-10-20

## Status

Accepted

## Context

The recorder must run continuously in the background, start on boot, and recover from crashes, without depending on a terminal session.

## Alternatives Considered

* **`nohup` / `&`** — fragile, no restart, lost on reboot.
* **cron `@reboot`** — starts once, no supervision.
* **systemd service** — auto-start, restart on failure, journald logging.

## Decision

We will manage the recorder as a systemd service with `Restart=always`:

```ini
[Unit]
Description=Keylog
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/keylog/keylog.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

Enabled via `systemctl enable --now keylog.service`. The same unit pattern applies to the bpftrace variant by pointing `ExecStart` at a wrapper script.

## Consequences

* **Positive:** Survives reboot and crashes; logs accessible via `journalctl -u keylog.service`; standard Linux operations model.
* **Negative:** Runs as root; requires discipline to review the unit and script permissions.

