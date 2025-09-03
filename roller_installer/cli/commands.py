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
    from pathlib import Path
    from roller_installer.core.github_client import RollerGitHubClient
    from roller_installer.core.ubi_downloader import UbiDownloader
    
    console.print("[bold blue]ROLLER Installer[/bold blue]")
    console.print()
    
    # Set up installation directory - default to current directory
    install_path = Path(install_dir) if install_dir else Path.cwd()
    version_file = install_path / ".roller-version"
    
    try:
        # Get the release tag to install
        if not version:
            console.print("Checking for latest pre-release...")
            github_client = RollerGitHubClient()
            version = github_client.get_latest_prerelease_tag()
            if not version:
                console.print("[red]No pre-releases found[/red]")
                raise typer.Exit(1)
        
        # Check if already installed with same version
        if version_file.exists() and not force:
            current_version = version_file.read_text().strip()
            if current_version == version:
                console.print(f"[green]ROLLER {version} is already installed[/green]")
                console.print("Use --force to reinstall")
                return
        
        console.print(f"Installing ROLLER {version} to {install_path}")
        
        # Download using ubi
        downloader = UbiDownloader()
        binary_path = downloader.download(
            install_dir=install_path,
            tag=version,
            exe_name="roller",
            progress_callback=lambda msg: console.print(f"  {msg}")
        )
        
        # Save version info for update checking
        version_file = install_path / ".roller-version"
        version_file.write_text(version)
        
        console.print(f"[green]✅ ROLLER {version} installed successfully![/green]")
        console.print(f"Binary location: {binary_path}")
        
    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        raise typer.Exit(1)


@cli_app.command()
def check_updates(
    install_dir: Optional[str] = typer.Option(
        None, "--install-dir", help="Installation directory to check"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Check for ROLLER updates."""
    from pathlib import Path
    from roller_installer.core.github_client import RollerGitHubClient
    
    console.print("[bold blue]Checking for ROLLER Updates[/bold blue]")
    console.print()
    
    # Find installation directory
    check_path = Path(install_dir) if install_dir else Path.cwd()
    version_file = check_path / ".roller-version"
    
    if not version_file.exists():
        console.print("[yellow]No ROLLER installation found in this directory[/yellow]")
        console.print("Run 'roller-installer cli install' first")
        raise typer.Exit(1)
    
    try:
        current_version = version_file.read_text().strip()
        console.print(f"Current version: {current_version}")
        
        # Check for latest
        github_client = RollerGitHubClient()
        latest_version = github_client.get_latest_prerelease_tag()
        
        if not latest_version:
            console.print("[yellow]Could not check for updates[/yellow]")
            raise typer.Exit(1)
        
        if latest_version == current_version:
            console.print(f"[green]✅ You're up to date![/green]")
        else:
            console.print(f"[yellow]Update available: {latest_version}[/yellow]")
            console.print(f"Run 'roller-installer cli install' to update")
    
    except Exception as e:
        console.print(f"[red]Failed to check updates: {e}[/red]")
        raise typer.Exit(1)


@cli_app.command()
def list_releases(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of releases to show"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """List available ROLLER releases."""
    from roller_installer.core.github_client import RollerGitHubClient
    
    console.print("[bold blue]Available ROLLER Releases[/bold blue]")
    console.print()
    
    try:
        github_client = RollerGitHubClient()
        releases = github_client.list_releases(limit=limit, include_prerelease=True)
        
        if not releases:
            console.print("[yellow]No releases found[/yellow]")
            return
        
        table = Table(title=f"Latest {len(releases)} Releases")
        table.add_column("Tag", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Published", style="green")
        
        for release in releases:
            release_type = "Pre-release" if release['prerelease'] else "Stable"
            table.add_row(
                release['tag_name'],
                release_type,
                str(release['published_at'])
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Failed to list releases: {e}[/red]")
        raise typer.Exit(1)


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
