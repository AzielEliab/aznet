"""Allow ``python -m aznet`` to invoke the CLI."""

from aznet.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
