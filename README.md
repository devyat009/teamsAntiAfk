# Teams Anti-AFK Tray App

A lightweight, background Windows System Tray utility written in Python that automatically keeps your Microsoft Teams status **Available** by detecting periods of user inactivity, simulating realistic activity (opening a temporary text file in Notepad, typing keystrokes, gentle mouse movement, and closing), and providing an instant global stop/resume hotkey.

---

## Features

- **System Tray Integration**: Unobtrusive tray icon indicating live status:
  - 🟢 **Green**: Active & monitoring idle time.
  - 🔴 **Red**: Paused / Stopped.
  - 🟡 **Amber**: Currently executing Anti-AFK routine.
- **Windows Idle Detection**: Uses native Win32 `GetLastInputInfo` to monitor true hardware/system idle time with near-zero CPU and memory footprint.
- **4-Minute Default Threshold**: Automatically triggers when you are away for 4 minutes (configurable via tray menu to 1m, 2m, 4m, 5m, 10m).
- **Realistic Action Routine**:
  1. Opens a temporary `.txt` document in `Notepad.exe`.
  2. Types human-like keystrokes.
  3. Moves the mouse smoothly within a subtle bounding area.
  4. Gracefully closes Notepad without leaving unsaved files or prompts.
- **Instant Global Hotkey**:
  - `Win + Ctrl + Shift + F`: Instantly stops / pauses (or resumes) the anti-AFK service from anywhere in Windows.
- **Safe Interruption**: If the stop hotkey is pressed while a routine is in progress, it immediately halts typing and cleanly closes the temporary window.
- **Silent Background Run**: Option to run completely in the background without keeping a command prompt open.

---

## Keyboard Shortcuts

| Shortcut | Description |
| :--- | :--- |
| <kbd>Win</kbd> + <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>F</kbd> | **Toggle Anti-AFK (Stop / Resume)** |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Alt</kbd> + <kbd>F</kbd> | *(Secondary Fallback Shortcut)* |

---

## Installation & Requirements

- **OS**: Windows 10 / 11
- **Python**: Python 3.9+ (Fully compatible with Python 3.14)

### 1. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

---

## Usage

### Option 1: Standalone Executable (.EXE)
Run the compiled standalone executable (no Python installation required):
```bash
dist\TeamsAntiAfk.exe
```

### Option 2: Standard Launcher (With Console)
Double-click `run.bat` or run:
```bash
py main.py
```

### Option 3: Silent Background Launcher (No Console Window)
Double-click `run_hidden.vbs` or run:
```bash
pyw main.py
```

---

## Building Standalone EXE

To compile the application into a single standalone `.exe` with its embedded icon:
- **1-Click Build**: Double-click `build.bat`
- **Manual Command**:
  ```bash
  py -m PyInstaller --onefile --noconsole --icon=assets/icon.ico --name=TeamsAntiAfk --clean main.py
  ```
The output executable will be created at `dist/TeamsAntiAfk.exe`.

---

## System Tray Context Menu

Right-click the icon in your Windows Taskbar Notification Area (System Tray) to access:

- **Status**: Displays current operational status.
- **Pause / Resume Anti-AFK**: Toggle monitoring state.
- **Trigger Routine Now (Test)**: Instantly run the routine to verify mouse and typing simulation.
- **Idle Timeout**: Switch between 1 minute (for testing), 2 minutes, 4 minutes (default), 5 minutes, or 10 minutes.
- **Show Desktop Notifications**: Enable or disable Windows balloon notifications.
- **Exit**: Cleanly shut down the application.

---

## Project Structure

```
teamsAntiAfk/
├── assets/
│   └── icon.ico         # Application icon
├── dist/
│   └── TeamsAntiAfk.exe # Standalone executable (gitignored)
├── afk_actions.py       # Handles opening Notepad, typing, mouse movement, and cleanup
├── build.bat            # 1-Click PyInstaller build script
├── hotkey_manager.py    # Global hotkey listener for Win + Ctrl + Shift + F
├── idle_tracker.py      # Win32 API idle duration measurement
├── main.py              # Application entry point
├── requirements.txt     # Python package requirements
├── run.bat              # 1-Click batch launcher
├── run_hidden.vbs       # Silent background VBS launcher
├── tray_app.py          # System tray icon, state machine, and context menu
└── tests/
    └── test_components.py # Unit and integration tests
```

---

## Running at Windows Startup (Optional)

To start the app automatically when Windows boots:
1. Press <kbd>Win</kbd> + <kbd>R</kbd>, type `shell:startup`, and press **Enter**.
2. Create a shortcut to `run_hidden.vbs` inside that folder.