"""
Module: idle_tracker.py
Provides functionality to get system idle time on Windows using ctypes and Win32 APIs.
"""

import ctypes
from ctypes import Structure, c_uint, sizeof, byref


class LASTINPUTINFO(Structure):
    _fields_ = [
        ("cbSize", c_uint),
        ("dwTime", c_uint),
    ]


def get_idle_seconds() -> float:
    """
    Returns the time elapsed in seconds since the last physical input event
    (keyboard, mouse movement, mouse clicks).
    """
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = sizeof(LASTINPUTINFO)

    if not ctypes.windll.user32.GetLastInputInfo(byref(last_input_info)):
        return 0.0

    # GetTickCount64 prevents 49.7 day rollover issues present in GetTickCount
    try:
        current_tick = ctypes.windll.kernel32.GetTickCount64()
    except AttributeError:
        current_tick = ctypes.windll.kernel32.GetTickCount()

    # dwTime is a 32-bit unsigned integer (milliseconds)
    # Perform modular arithmetic to handle 32-bit wrap-around correctly if GetTickCount64 was used
    current_tick_32 = current_tick & 0xFFFFFFFF
    dw_time = last_input_info.dwTime & 0xFFFFFFFF

    if current_tick_32 >= dw_time:
        millis = current_tick_32 - dw_time
    else:
        millis = (0xFFFFFFFF - dw_time) + current_tick_32

    return max(0.0, millis / 1000.0)


if __name__ == "__main__":
    import time
    print(f"Current idle time: {get_idle_seconds():.2f} seconds")
    print("Waiting 3 seconds...")
    time.sleep(3)
    print(f"Idle time after 3s sleep: {get_idle_seconds():.2f} seconds")
