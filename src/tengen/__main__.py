"""Command-line interface."""
import click


@click.command()
@click.option(
    "--file-name",
    "-f",
    help="Output file name.",
    default="ds.nc",
    type=click.Path(writable=True),
)
@click.option(
    "--identifier",
    "-i",
    help="Atmospheric profile identifier.",
    required=True,
    type=click.Choice(
        ["thuillier_2003", "coddington_2021"],
        case_sensitive=True,
    ),
)
@click.version_option()
def main(file_name: str, identifier: str) -> None:
    """Tengen."""


if __name__ == "__main__":
    main(prog_name="tengen")  # pragma: no cover
