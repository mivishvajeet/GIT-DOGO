"""CLI entrypoint module."""

import sys
from .menu import DojoCli


def main() -> None:
    try:
        app = DojoCli()
        app.run()
    except KeyboardInterrupt:
        print("\n\nOperation aborted by user. Exiting Git Dojo.")
        sys.exit(0)


if __name__ == "__main__":
    main()
