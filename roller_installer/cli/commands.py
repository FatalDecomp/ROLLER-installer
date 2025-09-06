"""
CLI commands for ROLLER installer using Typer.
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from ..utils.icons import ICONS

# Create the main app and console
app = typer.Typer(
    help="ROLLER Installer - Install and manage ROLLER (Fatal Racing decompilation)",
    no_args_is_help=False,
)
console = Console()

# Create CLI subcommand app
cli_app = typer.Typer(help="Command-line interface for ROLLER installer")


def _ensure_tools_available(verbose: bool = False):
    """Ensure all required tools are available, download if needed."""
    from roller_installer.utils.binary_resolver import ToolManager
    
    tool_manager = ToolManager()
    
    # First check availability for verbose output
    if verbose:
        availability = tool_manager.check_tools_availability()
        for tool_name, info in availability.items():
            if info['available']:
                if info['location'] == 'installed':
                    console.print(f"  {ICONS['check']} {tool_name} ready at: {info['path']}")
                else:
                    console.print(f"  {ICONS['check']} {tool_name} found in system: {info['path']}")
    
    # Ensure tools are available
    def progress_callback(message: str):
        if verbose:
            console.print(f"  {message}")
        else:
            console.print(message)
    
    results = tool_manager.ensure_tools_available(progress_callback=progress_callback)
    
    # Count successes and report
    success_count = sum(1 for result in results.values() if result['success'])
    total_count = tool_manager.get_tool_count()
    
    if verbose:
        for tool_name, result in results.items():
            if result['success']:
                if not result['was_installed']:
                    # Was already available, we showed this above
                    pass
                else:
                    console.print(f"  {ICONS['check']} {tool_name} ready")
            else:
                console.print(f"  {ICONS['warning']}  {tool_name} failed: {result['error']}")
    
    if success_count < total_count:
        console.print(f"  {ICONS['warning']}  Some tools may not be available, but installation will continue")
    elif verbose:
        console.print(f"  {ICONS['check']} All tools ready")


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

        # Ensure required tools are available
        if verbose:
            console.print(f"{ICONS['tools']} Ensuring required tools are available...")
        _ensure_tools_available(verbose=verbose)

        # Download using ubi
        downloader = UbiDownloader()
        binary_path = downloader.download(
            install_dir=install_path,
            tag=version,
            exe_name="roller",
            progress_callback=lambda msg: console.print(f"  {msg}"),
        )

        # Save version info for update checking
        version_file = install_path / ".roller-version"
        version_file.write_text(version)

        console.print(f"[green]{ICONS['success']} ROLLER {version} installed successfully![/green]")
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
            console.print(f"[green]{ICONS['success']} You're up to date![/green]")
        else:
            console.print(f"[yellow]Update available: {latest_version}[/yellow]")
            console.print("Run 'roller-installer cli install' to update")

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
            release_type = "Pre-release" if release["prerelease"] else "Stable"
            table.add_row(
                release["tag_name"], release_type, str(release["published_at"])
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Failed to list releases: {e}[/red]")
        raise typer.Exit(1)


@cli_app.command()
def extract_assets(
    source: str = typer.Argument(
        ..., help="Path to ZIP or ISO file containing FATDATA"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output directory (default: current directory)"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Extract FATDATA directory from ZIP or ISO files."""
    from pathlib import Path
    from roller_installer.core.asset_extractor import extract_fatdata

    console.print("[bold blue]ROLLER Asset Extractor[/bold blue]")
    console.print()

    source_path = Path(source)
    if not source_path.exists():
        console.print(f"[red]Source file not found: {source_path}[/red]")
        raise typer.Exit(1)

    # Set output directory
    output_path = Path(output_dir) if output_dir else Path.cwd()

    try:
        console.print(f"Extracting FATDATA from: {source_path}")
        console.print(f"Output directory: {output_path}")
        console.print()

        result = extract_fatdata(source_path, output_path)

        console.print(f"[green]{ICONS['success']} Successfully extracted FATDATA![/green]")
        console.print(f"Location: {result.fatdata_path}")

        if result.has_music:
            console.print(
                f"[green]🎵 Also extracted {len(result.music_paths)} music tracks[/green]"
            )

        # Show contents if verbose
        if verbose and result.fatdata_path.exists():
            console.print("\n[bold]FATDATA contents:[/bold]")
            file_count = 0
            for item in sorted(result.fatdata_path.rglob("*")):
                if item.is_file():
                    relative = item.relative_to(result.fatdata_path)
                    size = item.stat().st_size
                    console.print(f"  {relative} ({size:,} bytes)")
                    file_count += 1
            console.print(f"\nTotal files extracted: {file_count}")

    except Exception as e:
        console.print(f"[red]Extraction failed: {e}[/red]")
        if verbose:
            import traceback

            console.print(f"[red]{traceback.format_exc()}[/red]")
        raise typer.Exit(1)


@cli_app.command("download-tools")
def download_tools(
    force: bool = typer.Option(
        False, "--force", help="Force re-download even if tools already exist"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Download external tools (ubi, bchunk) to the tools directory."""
    from roller_installer.utils.binary_resolver import ToolManager
    
    console.print("[bold blue]ROLLER Installer - Download Tools[/bold blue]")
    console.print()
    
    tool_manager = ToolManager()
    
    # Get tool descriptions for display
    tool_descriptions = {
        "ubi": "Universal Binary Installer for downloading ROLLER releases",
        "bchunk": "Disc image conversion tool for CUE/BIN files",
    }
    
    def progress_callback(message: str):
        if verbose:
            console.print(f"  {message}")
    
    results = tool_manager.download_tools(force=force, progress_callback=progress_callback)
    
    success_count = 0
    total_count = tool_manager.get_tool_count()
    
    for tool_name in tool_manager.get_tool_names():
        result = results[tool_name]
        description = tool_descriptions.get(tool_name, "External tool")
        
        console.print(f"[cyan]• {tool_name}[/cyan] - {description}")
        
        try:
            if result['success']:
                if result['already_existed'] and not result['was_downloaded']:
                    # Tool already existed and wasn't re-downloaded
                    path = result['path']
                    if path.parent.name == 'tools':
                        console.print(f"  {ICONS['check']} [green]Already installed at:[/green] {path}")
                    else:
                        console.print(f"  {ICONS['check']} [green]Found in system at:[/green] {path}")
                        console.print(f"  {ICONS['info']}  Use --force to download to tools/ directory anyway")
                else:
                    # Tool was downloaded/installed
                    console.print(f"  {ICONS['success']} [bold green]Downloaded successfully:[/bold green] {result['path']}")
                
                # Test the tool if verbose
                if verbose and result.get('working') is True:
                    console.print(f"  {ICONS['check']} [green]{tool_name} is working correctly[/green]")
                elif verbose and result.get('working') is False:
                    console.print(f"  {ICONS['warning']}  [yellow]{tool_name} may not be working correctly[/yellow]")
                
                success_count += 1
            else:
                console.print(f"  {ICONS['error']} [red]{result['error']}[/red]")
                
        except Exception as e:
            console.print(f"  {ICONS['error']} [red]Error processing {tool_name}: {str(e)}[/red]")
            if verbose:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        console.print()
    
    # Summary
    if success_count == total_count:
        console.print(f"{ICONS['success']} [bold green]All {total_count} tools are ready![/bold green]")
    elif success_count > 0:
        console.print(f"{ICONS['warning']}  [yellow]{success_count}/{total_count} tools are ready[/yellow]")
        console.print("Some tools may not be available or failed to download.")
    else:
        console.print(f"{ICONS['error']} [bold red]No tools were successfully downloaded[/bold red]")
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
    console.print(f"{ICONS['success']} Arguments parsed successfully!")


def gui():
    """Launch the GUI installer (default behavior)."""
    console.print(f"[bold green]{ICONS['rocket']} Launching ROLLER Installer GUI...[/bold green]")
    console.print(f"[yellow]{ICONS['warning']}  GUI not implemented yet - coming soon![/yellow]")


@app.command()
def tui():
    """Launch the text-based user interface installer."""
    console.print(f"[bold blue]{ICONS['desktop']}  Launching ROLLER Installer TUI...[/bold blue]")
    console.print(f"[yellow]{ICONS['warning']}  TUI not implemented yet - coming soon![/yellow]")


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
