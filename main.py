"""
Teams Anti-AFK Application
Entry point for starting the system tray application.
"""

import sys
import os

from tray_app import TeamsAntiAfkTrayApp


def main():
    try:
        app = TeamsAntiAfkTrayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting Teams Anti-AFK...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
