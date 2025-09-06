# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**IMPORTANT**: This project uses `poetry` for dependency management. NEVER use `pip` directly or run `python` without `poetry run`. Always use the mise tasks or poetry commands.

```bash
# Install dependencies (REQUIRED before running anything)
mise run deps
# or: poetry install

# Run the installer in development (ALWAYS use poetry run or mise tasks)
mise run installer -- --help
mise run installer -- install --version v1.0.0
# or: poetry run python -m roller_installer --help

# Build native binary
mise run build
# or: poetry run python scripts/build.py
# Output: dist/roller-installer (or .exe on Windows)

# Test GitHub Actions locally
mise run test-github-workflows
# or: act

# Install CI dependencies
mise run install:ci
```

**DO NOT USE:**
- `pip install` - Use `poetry add` or `poetry install` instead
- `python -m roller_installer` - Use `poetry run python -m roller_installer` or `mise run installer`
- Direct python execution without poetry

## Project Architecture

**ROLLER Installer** is a cross-platform installer for ROLLER (Fatal Racing/Whiplash decompilation) built with Python. The project structure follows a modular design:

### Entry Points
- `main.py`: Standalone entry point for PyInstaller binary building
- `roller_installer/__main__.py`: Python module entry point (`python -m roller_installer`)
- `roller_installer/cli/commands.py`: Typer-based CLI implementation with Rich terminal output

### Package Structure
- `roller_installer/cli/`: CLI interface using Typer and Rich for professional command-line experience
- `roller_installer/core/`: Core installer logic (planned - GitHub integration, installation, asset extraction)
- `roller_installer/gui/`: GUI interface (planned - tkinter wizard)
- `roller_installer/tui/`: TUI interface (planned - retro DOS-style installer)
- `roller_installer/utils/`: Shared utilities (planned)

### Configuration Templates
- `assets/templates/FATAL.INI`: Game configuration template (audio, video, controls)
- `assets/templates/config.ini`: Sound/language configuration template

### Current Implementation Status
- ✅ CLI framework with Typer (all commands structured but not implemented)
- ✅ Build system with PyInstaller for native binaries
- ✅ Project structure and packaging
- 📋 GitHub API integration for downloading ROLLER releases
- 📋 Installation logic and configuration generation
- 📋 Asset extraction from ZIP/ISO files

### Key Features (Planned)
1. **Multi-Interface Support**: CLI (current), GUI wizard, retro TUI
2. **GitHub Integration**: Download ROLLER binaries from GitHub releases, update checking
3. **Asset Management**: Extract FATDATA from folders, ZIP files, or ISO images
4. **Cross-Platform Installation**: Windows, macOS, Linux with proper shortcuts and file associations
5. **Configuration Generation**: Create game config files with sensible defaults
6. **Self-Updating**: Installer can update itself from GitHub releases

### Dependencies
- **Runtime**: `typer` (CLI), `pygithub` (GitHub API)
- **Development**: `pyinstaller` (binary building), `ruff` (linting)
- **Python**: 3.9+ (PyInstaller compatibility)

The installer follows a three-phase approach: download ROLLER binary from GitHub, extract game assets from user's Fatal Racing installation, and generate configuration files for optimal gameplay experience.
