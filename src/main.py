"""Application entry point."""

from src.gui import Terminal
from src.shell import Shell


def main():
    """Run the graphical shell."""
    Terminal(Shell()).run()


if __name__ == "__main__":
    main()
