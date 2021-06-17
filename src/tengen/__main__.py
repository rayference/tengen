"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Tengen."""


if __name__ == "__main__":
    main(prog_name="tengen")  # pragma: no cover
