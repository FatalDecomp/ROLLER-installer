"""
CLI commands for ROLLER installer using Typer.
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

# Create the main app and console
app = typer.Typer(
    help="ROLLER Installer - Install and manage ROLLER (Fatal Racing decompilation)",
    no_args_is_help=False,
)
console = Console()

# Create CLI subcommand app
cli_app = typer.Typer(help="Command-line interface for ROLLER installer")


@cli_app.command()
def install(
    version: Optional[str] = typer.Option(
        None, "--version", "-v", help="Specific version to install (e.g., v1.2.3)"
    ),
    install_dir: Optional[str] = typer.Option(
        None, "--install-dir", help="Custom installation directory"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force reinstall even if already installed"
    ),
    no_shortcuts: bool = typer.Option(
        False, "--no-shortcuts", help="Skip creating desktop shortcuts"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Install ROLLER binary from GitHub releases."""
    console.print("[bold blue]ROLLER Installer - Install Command[/bold blue]")
    console.print()

    # Create table to display parsed arguments
    table = Table(title="Parsed Arguments")
    table.add_column("Argument", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("version", str(version))
    table.add_row("install_dir", str(install_dir))
    table.add_row("force", str(force))
    table.add_row("no_shortcuts", str(no_shortcuts))
    table.add_row("verbose", str(verbose))

    console.print(table)
    console.print()
    console.print("✅ Arguments parsed successfully!")


@cli_app.command()
def check_updates(
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Check for ROLLER updates."""
    console.print("[bold blue]ROLLER Installer - Check Updates Command[/bold blue]")
    console.print()

    table = Table(title="Parsed Arguments")
    table.add_column("Argument", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("verbose", str(verbose))

    console.print(table)
    console.print()
    console.print("✅ Arguments parsed successfully!")


@cli_app.command()
def list_releases(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of releases to show"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """List available ROLLER releases."""
    console.print("[bold blue]ROLLER Installer - List Releases Command[/bold blue]")
    console.print()

    table = Table(title="Parsed Arguments")
    table.add_column("Argument", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("limit", str(limit))
    table.add_row("verbose", str(verbose))

    console.print(table)
    console.print()
    console.print("✅ Arguments parsed successfully!")


@cli_app.command("self-update")
def self_update(
    check_only: bool = typer.Option(
        False, "--check-only", help="Only check for updates, do not install"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Update the installer itself to the latest version."""
    console.print("[bold blue]ROLLER Installer - Self-Update Command[/bold blue]")
    console.print()

    table = Table(title="Parsed Arguments")
    table.add_column("Argument", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("check_only", str(check_only))
    table.add_row("verbose", str(verbose))

    console.print(table)
    console.print()
    console.print("✅ Arguments parsed successfully!")


def gui():
    """Launch the GUI installer (default behavior)."""
    console.print("[bold green]🚀 Launching ROLLER Installer GUI...[/bold green]")
    console.print("[yellow]⚠️  GUI not implemented yet - coming soon![/yellow]")


@app.command()
def tui():
    """Launch the text-based user interface installer."""
    console.print("[bold blue]🖥️  Launching ROLLER Installer TUI...[/bold blue]")
    console.print("[yellow]⚠️  TUI not implemented yet - coming soon![/yellow]")


# Add CLI subcommand to main app
app.add_typer(cli_app, name="cli")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """ROLLER Installer - Install and manage ROLLER (Fatal Racing decompilation).

    By default, launches the GUI installer. Use subcommands for CLI or TUI interfaces.
    """
    if ctx.invoked_subcommand is None:
        # Default behavior: launch GUI
        gui()


def cli_main():
    """Entry point for the CLI that doesn't require context."""
    app()


if __name__ == "__main__":
    main()
