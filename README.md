# ROLLER Installer

A cross-platform installer for [ROLLER](https://github.com/FatalDecomp/ROLLER) (Fatal Racing/Whiplash decompilation) that automatically downloads the game binaries and extracts assets from your original game files.

## What it does

ROLLER Installer simplifies the process of setting up the ROLLER decompilation:

1. **Downloads ROLLER binaries** from GitHub releases automatically
2. **Extracts game assets** from your original Fatal Racing/Whiplash files (ZIP, ISO, or CUE/BIN format)
3. **Sets up the installation** with proper configuration files
4. **Manages updates** and version tracking

## Installation

### Download Pre-built Binary
Download the latest release for your platform from [GitHub Releases](https://github.com/FatalDecomp/ROLLER-installer/releases):
- Windows: `roller-installer.exe`
- macOS: `roller-installer` (Intel/Apple Silicon)
- Linux: `roller-installer`

### From Source
See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup instructions.

## Prerequisites

The installer requires these external tools (automatically detected):
- **`ubi`** (Universal Binary Installer) - Required for downloading ROLLER binaries
- **`bchunk`** (optional) - Only needed for CUE/BIN disc image support

## Quick Start

### Install ROLLER (latest version)
```bash
roller-installer cli install
```

### Extract assets from your original game files
```bash
# From a ZIP file
roller-installer cli extract-assets game.zip

# From an ISO disc image
roller-installer cli extract-assets game.iso

# From CUE/BIN files
roller-installer cli extract-assets game.cue
```

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `install` | Install ROLLER binary | `roller-installer cli install` |
| `extract-assets` | Extract FATDATA from game files | `roller-installer cli extract-assets game.zip` |
| `check-updates` | Check for newer ROLLER versions | `roller-installer cli check-updates` |
| `list-releases` | Show available ROLLER releases | `roller-installer cli list-releases` |
| `self-update` | Update the installer itself | `roller-installer cli self-update` |

### Common Options
```bash
# Install specific version
roller-installer cli install --version nightly-0.0.0-126f00d

# Custom installation directory  
roller-installer cli install --install-dir /opt/roller

# Force reinstall
roller-installer cli install --force

# Verbose output
roller-installer cli extract-assets game.iso --verbose

# Show help
roller-installer --help
```

## Supported Formats

The installer can extract FATDATA directories from:
- **ZIP files** - Standard ZIP archives containing game files
- **ISO images** - Disc images from CD-ROM versions  
- **CUE/BIN files** - Raw disc images with separate audio tracks

## Contributing

Want to contribute to ROLLER Installer development? See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup and build instructions
- Project architecture and technical details
- Guidelines for adding new features
- Code style and testing information

## License

[License information]
