"""
Module: afk_actions.py
Implements the anti-AFK activity routine:
- Opens a terminal window (cmd.exe) without creating any temporary files on disk.
- Simulates natural keystrokes.
- Simulates smooth mouse movement.
- Closes the terminal cleanly.
"""

import time
import random
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
    1. Opens a standalone terminal (cmd.exe) with zero temporary disk files.
    2. Types realistic activity commands/text.
    3. Performs slight mouse movement.
    4. Exits and always ensures the terminal process is cleanly closed in a finally block.

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

    proc = None
    success = False

    try:
        log("Opening terminal window (cmd.exe)...")
        # Launch standalone console window without creating any temporary file on disk
        proc = subprocess.Popen(
            ["cmd.exe"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        time.sleep(1.2)  # Allow terminal window to open and receive focus

        if stop_event and stop_event.is_set():
            log("Stop event detected during startup.")
            return False

        # 1. Keystroke simulation
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        phrases = [
            f"echo [Teams Anti-AFK] Heartbeat at {timestamp_str}\n",
            "echo Refreshing active session status...\n",
            "echo Teams Anti-AFK session active\n",
        ]
        chosen_phrase = random.choice(phrases)

        log("Simulating keystrokes in terminal...")
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

        # 3. Exit terminal command
        if stop_event and stop_event.is_set():
            log("Stop event detected before exit.")
            return False

        log("Sending exit command to terminal...")
        pyautogui.write("exit\n")
        time.sleep(0.5)

        success = True
        return True

    except Exception as ex:
        log(f"Error during anti-AFK routine: {ex}")
        return False

    finally:
        # ALWAYS guarantee that the terminal process tree is cleanly terminated
        log("Cleaning up: ensuring terminal process is terminated...")
        _cleanup_terminal_process(proc, log)
        if success:
            log("Anti-AFK routine completed and closed successfully.")


def _cleanup_terminal_process(proc: subprocess.Popen, log_func=None):
    """
    Forcefully and cleanly terminates the terminal process tree.
    """
    def log(m):
        if log_func:
            log_func(m)

    if proc:
        try:
            # Terminate the process tree (including any child threads/consoles)
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


if __name__ == "__main__":
    print("Testing anti-AFK routine with terminal (zero temp files)...")
    result = perform_anti_afk_routine()
    print("Routine result:", result)
