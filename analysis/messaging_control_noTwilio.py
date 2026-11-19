import socket
import struct
import sys
import termios
import tty

# =========================================================================
# Phone-send distraction markers (no Twilio) — all sets in one script
# =========================================================================
# Send the text (or play the ping) from YOUR phone. This script only stamps
# the EEG file. Same three event markers for every set:
#
#   1.0  notification onset (you tap Send / play the sound)
#  11.0  engagement starts  (pickup, glance, or they look despite Set 4)
#  12.0  engagement ends    (phone down / eyes back on the task)
#
# Analysis uses 1→11 as passive setup and 11→12 as the real distraction.
# At the start of a run this script also stamps 101–104 so the file records
# which set you were in.
#
# Pre-type the message, thumb on Send, other hand on [S]. Press S and Send
# together. Marker Widget UDP receive (not the Networking widget).
# In the GUI: add Marker, Receive IP / Port = these values, start recording first.

UDP_IP = "127.0.0.1"
UDP_PORT = 12350

SETS = {
    1: {
        "name": "Baseline (no phone)",
        "allow_send": False,
        "blurb": (
            "Do not send texts. You usually skip this script on baseline days.\n"
            "  If it is running anyway: [Q] quit. [S] and [Space] are disabled."
        ),
    },
    2: {
        "name": "Text + reply",
        "allow_send": True,
        "blurb": (
            "They receive a text and ARE allowed to reply.\n"
            "  [S] + Send together → marker 1.0 (text left your phone).\n"
            "  [Space] when they pick up → 11.0.  [Space] when they put it down after the reply → 12.0."
        ),
    },
    3: {
        "name": "Text + glance only (no reply)",
        "allow_send": True,
        "blurb": (
            "They receive a text and may glance. They should NOT reply.\n"
            "  [S] + Send together → marker 1.0.\n"
            "  [Space] when they glance at the phone → 11.0.\n"
            "  [Space] when eyes are back on the task → 12.0."
        ),
    },
    4: {
        "name": "Auditory ping, eyes on screen",
        "allow_send": True,
        "blurb": (
            "They hear the notification. Eyes should stay on the task.\n"
            "  [S] + Send (or play the ping) together → marker 1.0.\n"
            "  Do not press Space if they stay on screen (1→next 1 is passive only).\n"
            "  [Space] 11 / 12 only if they look at the phone anyway."
        ),
    },
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_gui_marker(val):
    """Send one big-endian float32 to the Marker widget (what the GUI actually parses)."""
    try:
        sock.sendto(struct.pack("!f", float(val)), (UDP_IP, UDP_PORT))
        print(f"   [UDP -> GUI {UDP_IP}:{UDP_PORT}] marker {float(val):g}")
    except Exception as e:
        print(f"   [ERROR] Failed to send network marker to GUI: {e}")


def get_key():
    """Captures a raw keypress instantaneously from standard terminal input."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def choose_set():
    if len(sys.argv) > 1 and sys.argv[1] in ("1", "2", "3", "4"):
        return int(sys.argv[1])
    print("Which set is this recording?")
    for n, spec in SETS.items():
        print(f"  [{n}]  {spec['name']}")
    print("Or pass it on the command line:  python analysis/messaging_control_noTwilio.py 2")
    while True:
        raw = input("Set 1-4: ").strip()
        if raw in ("1", "2", "3", "4"):
            return int(raw)
        print("  type 1, 2, 3, or 4")


print("=============================================================")
print("  OpenBCI distraction marker (send the text from your phone)")
print(f"  Markers -> {UDP_IP}:{UDP_PORT}  (Marker widget Receive IP/Port)")
print("=============================================================")
set_id = choose_set()
spec = SETS[set_id]
print("-------------------------------------------------------------")
print(f"  SET {set_id}: {spec['name']}")
print(spec["blurb"])
print("  Analysis:  1→11 passive setup   11→12 real distraction")
print("Hotkeys:  [S] onset   [Space] engage/release   [Q] quit")
print("Start OpenBCI recording, then this script stamps the set id.")
print("-------------------------------------------------------------")

send_gui_marker(100.0 + set_id)  # 101, 102, 103, or 104
print(f"   set stamp {100 + set_id:g} is in the file. You can send events now.")

window_active = False

while True:
    key = get_key().lower()

    if key == "s":
        if not spec["allow_send"]:
            print("\n[SET 1] Baseline — not sending a 1.0. Switch set or press Q.")
            continue
        print("\n[ONSET] Stamp marker 1.0 — tap Send / play the ping now.")
        send_gui_marker(1.0)

    elif key == " ":
        if set_id == 1:
            print("\n[SET 1] Baseline — no 11/12 window. Press Q to quit.")
            continue
        if not window_active:
            if set_id == 4:
                print("\n[WINDOW 11] They looked at the phone (Set 4 break).")
            elif set_id == 3:
                print("\n[WINDOW 11] Glance started.")
            else:
                print("\n[WINDOW 11] Pickup / they engaged with the phone.")
            send_gui_marker(11.0)
            window_active = True
        else:
            print("\n[WINDOW 12] Eyes back / phone down.")
            send_gui_marker(12.0)
            window_active = False

    elif key == "q":
        if window_active:
            print("\n[WINDOW 12] Auto-close before quit.")
            send_gui_marker(12.0)
            window_active = False
        print("\nShutting down controller loop. Terminating network streams.")
        break
