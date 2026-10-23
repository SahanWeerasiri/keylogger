# Keylogger

A minimal Linux keystroke recorder built on Python and `evdev`, supervised by
systemd. It reads directly from the keyboard device file, so it keeps recording
across display-server changes and during the lock screen.

> **Scope:** This project captures keystrokes at the device level for local,
> authorized use (learning, self-monitoring, lab forensics). It does **not**
> implement clipboard semantics, and it does **not** include an auditd path.
> Kernel/device-level keylogging is a known MITRE ATT&CK technique
> (T1056.001); run it only on systems you own or are explicitly authorized to
> monitor.

---

## How It Works

```
keyboard hardware
      │
      ▼
kernel input subsystem (input_event)
      │
      ▼
/dev/input/by-path/...-event-kbd
      │
      ▼
src/keylog.py  ──►  /var/log/keylog.log
      ▲
      │
systemd (keylog.service)  — starts on boot, restarts on failure
```

Because capture happens at the device/kernel boundary, it is independent of
Wayland/X11 and of whether the session is locked. Character reconstruction from
key codes is intentionally left out of the recorder; the log stores timestamps
and key codes.

---

## 📁 Project Structure

```
.
├── .agents/                      # AI assistant rules, skills, workflows
│   ├── rules/                    # common + language-specific guidelines
│   ├── skills/                   # AI agent skills
│   └── workflows/                # AI agent workflows
├── .github/                      # CI workflows and PR template
├── .githooks/                    # Tracked git hooks (pre-commit secret scan)
├── .editorconfig                 # Cross-IDE formatting standards
├── .gitignore                    # Multi-language gitignore
├── .gitleaksignore               # Secret scanning baseline exclusions
├── .venv/                        # Local virtualenv (not committed)
├── AGENTS.md                     # AI pairing guidelines
├── README.md                     # This file
├── docs/
│   └── adr/                      # Architecture Decision Records
├── keylog.log                    # Sample/working capture output
└── src/
    └── keylog.py                 # evdev recorder
```

Note: the service unit lives outside the repo (system-level). See
[Installation](#-installation).

---

## 🚀 Setup

### Step 1: Create a virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install evdev
```

### Step 2: Find your keyboard device

```bash
ls /dev/input/by-path/ | grep kbd
# example: platform-i8042-serio-0-event-kbd
```

Update `DEV` in `src/keylog.py` if your path differs from the default.

### Step 3: Grant access

Reading `/dev/input/event*` requires membership in the `input` group or root:

```bash
sudo usermod -aG input "$USER"
# log out and back in for the group change to take effect
```

### Step 4: Run it

Foreground (for testing):

```bash
python3 src/keylog.py
```

### Step 5: Enable the pre-commit secret scan (repo hygiene)

```bash
git config core.hooksPath .githooks
```

---

## 🔧 Background Operation (systemd)

Create `/etc/systemd/system/keylog.service`:

```ini
[Unit]
Description=Keylog
After=multi-user.target

[Service]
Type=simple
ExecStart=/path/to/venv/bin/python3 /path/to/keylogger/src/keylog.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now keylog.service
```

Inspect logs:

```bash
sudo systemctl status keylog.service
sudo journalctl -u keylog.service -f
sudo tail -f /var/log/keylog.log
```

Stop / disable:

```bash
sudo systemctl disable --now keylog.service
```

---

## 📝 Output Format

Append-only plain text, one line per key-down event:

```
<timestamp> <keycode>
```

Example:

```
1697993200.123456 KEY_A
1697993200.234567 KEY_B
```

Each line is flushed immediately so data survives a crash. Character
reconstruction from key codes depends on the active keyboard layout at capture
time and is left to post-processing.

---

## 🧭 Design Decisions

Significant choices are recorded as ADRs in [`docs/adr/`](docs/adr/):

| ADR | Title |
|-----|-------|
| 0001 | Use eBPF/bpftrace for Kernel-Level Keystroke Capture (exploration) |
| 0002 | Prefer Python + evdev over eBPF for the Usable Recorder |
| 0003 | Use systemd for Background Operation and Auto-Restart |
| 0004 | Capture at the Kernel/Device Level to Survive Lock Screen |
| 0005 | Store Output as Timestamped Scancode/Keycode Logs |
| 0006 | Project Structure: Plain Python + systemd, No Custom eBPF Loader |

The eBPF/bpftrace one-liner is documented as an alternative operating mode in
ADR-0001; it is not part of the shipped code. The auditd/`pam_tty_audit` path is
intentionally out of scope for this project.

---

## 🛡️ Operational Notes

* **Privileges:** the recorder needs root or `input` group access; the systemd
  unit runs as root for simplicity.
* **Log rotation:** `keylog.log` grows unbounded. Add a `logrotate` rule if you
  keep it running long-term.
* **Detection:** device-level key capture is indistinguishable from a malicious
  keylogger to EDR/security tooling. Only deploy where you have authorization.
* **No clipboard:** the kernel cannot see user-space selected text, so
  clipboard-style capture is not a goal of this project.

---

## 🧹 Uninstall

```bash
sudo systemctl disable --now keylog.service
sudo rm /etc/systemd/system/keylog.service
sudo systemctl daemon-reload
sudo rm -f /var/log/keylog.log
```