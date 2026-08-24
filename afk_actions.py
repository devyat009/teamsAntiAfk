"""
Module: afk_actions.py
Implements the anti-AFK activity routine:
- Opens a temporary .txt file in Notepad.
- Simulates natural keystrokes.
- Simulates smooth mouse movement.
- Closes Notepad and reliably removes the temporary file.
"""

import os
import time
import random
import tempfile
import subprocess
import datetime
import threading
import pyautogui

# Disable fail-safe to prevent crash when mouse cursor moves near display edges
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


def perform_anti_afk_routine(stop_event: threading.Event = None, log_callback=None) -> bool:
    """
    Executes the anti-AFK activity sequence:
    1. Creates a temporary .txt file
    2. Opens Notepad with the file
    3. Types realistic activity text
    4. Performs slight mouse movement
    5. Always closes Notepad and deletes the temporary file in a finally block.

    Returns True if completed successfully, False if aborted by stop_event or error.
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(f"[Anti-AFK Action] {msg}")

    if stop_event and stop_event.is_set():
        log("Action aborted before starting (stop event set).")
        return False

    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"teams_anti_afk_{int(time.time())}_{random.randint(1000, 9999)}.txt")
    proc = None
    success = False

    try:
        # Create empty temp text file
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write("")

        log(f"Opening Notepad with temporary file: {temp_file_path}")
        proc = subprocess.Popen(["notepad.exe", temp_file_path])
        time.sleep(1.2)  # Allow Notepad window to open and receive focus

        if stop_event and stop_event.is_set():
            log("Stop event detected during startup.")
            return False

        # 1. Keystroke simulation
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        phrases = [
            f"Teams Anti-AFK activity heartbeat at {timestamp_str}\n",
            "Refreshing Teams status...\n",
            "Keeping active session...\n",
        ]
        chosen_phrase = random.choice(phrases)

        log("Simulating keystrokes...")
        for char in chosen_phrase:
            if stop_event and stop_event.is_set():
                log("Stop event detected during typing.")
                return False
            pyautogui.write(char)
            time.sleep(random.uniform(0.02, 0.05))

        time.sleep(0.4)

        # 2. Mouse movement simulation
        log("Simulating mouse movement...")
        current_x, current_y = pyautogui.position()
        screen_w, screen_h = pyautogui.size()

        offsets = [
            (random.randint(20, 50), random.randint(-25, 25)),
            (random.randint(-50, -20), random.randint(-25, 25)),
            (random.randint(-25, 25), random.randint(20, 45)),
            (random.randint(-25, 25), random.randint(-45, -20)),
        ]

        for dx, dy in offsets:
            if stop_event and stop_event.is_set():
                log("Stop event detected during mouse movement.")
                return False
            target_x = max(60, min(screen_w - 60, current_x + dx))
            target_y = max(60, min(screen_h - 60, current_y + dy))
            pyautogui.moveTo(target_x, target_y, duration=0.2)
            time.sleep(0.1)

        time.sleep(0.5)
        success = True
        return True

    except Exception as ex:
        log(f"Error during anti-AFK routine: {ex}")
        return False

    finally:
        # ALWAYS guarantee that Notepad is closed and temporary file is deleted
        log("Cleaning up: closing Notepad and removing temporary file...")
        _cleanup_notepad_and_file(proc, temp_file_path, log)
        if success:
            log("Anti-AFK routine completed and cleaned up successfully.")


def _cleanup_notepad_and_file(proc: subprocess.Popen, file_path: str, log_func=None):
    """
    Forcefully and cleanly terminates Notepad process tree and removes the temp file with retries.
    """
    def log(m):
        if log_func:
            log_func(m)

    # 1. Close Notepad process tree
    if proc:
        try:
            # Use taskkill /F /T to terminate the process and all child threads/windows
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception as e:
            log(f"taskkill error: {e}")

        try:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=1.0)
        except Exception:
            pass

    # Give Windows filesystem a moment to release file handles
    time.sleep(0.3)

    # 2. Reliably delete the temporary file with retry loop
    if file_path and os.path.exists(file_path):
        deleted = False
        for attempt in range(10):
            try:
                os.remove(file_path)
                deleted = True
                break
            except Exception as ex:
                time.sleep(0.25)

        if deleted:
            log(f"Temporary file successfully deleted: {file_path}")
        else:
            log(f"Warning: Could not delete temporary file {file_path} after retries.")


if __name__ == "__main__":
    print("Testing anti-AFK routine with guaranteed cleanup...")
    result = perform_anti_afk_routine()
    print("Routine result:", result)
