# Contributing to ROLLER Installer

Thank you for your interest in contributing to ROLLER Installer! This guide covers the technical architecture, development setup, and contribution guidelines for developers.

## Development Setup

### Prerequisites

- **Python 3.9-3.14** (compatible with PyInstaller)
- **Poetry 2+** for dependency management
- **mise** (for task running) - optional but recommended
- **External Tools**:
  - `ubi` (Universal Binary Installer) - Required for downloading ROLLER binaries
  - `bchunk` (optional) - Required for CUE/BIN disc image support

### Installation

#### Clone and Install Dependencies
```bash
# Clone the repository
git clone https://github.com/FatalDecomp/ROLLER-installer.git
cd ROLLER-installer

# Install with Poetry (recommended)
poetry install

# Install development dependencies
poetry install --with dev,lint
```

#### Install External Tools
```bash
# Install ubi (Universal Binary Installer)
# See: https://github.com/houseabsolute/ubi

# Install bchunk (for CUE/BIN support)
# Ubuntu/Debian: sudo apt install bchunk
# macOS: brew install bchunk
# Windows: Download from sourceforge
```

### Development Commands

This project uses `mise` for task management. Key commands:

```bash
# Run installer from source
mise run installer -- --help
mise run installer -- install --version v1.0.0

# Build native binary
mise run build-installer
# Output: dist/roller-installer (or .exe on Windows)

# Test built binary
./dist/roller-installer --help


# Lint and format code
ruff check .
ruff format .

# Test GitHub Actions locally
mise run test-github-workflows
# or: act
```

### Alternative Commands (without mise)
```bash
# Run from source
python -m roller_installer --help

# Build binary with PyInstaller
poetry run pyinstaller --onefile --name roller-installer --clean main.py

# Run with Poetry
poetry run python -m roller_installer cli install

```

## Project Architecture

ROLLER Installer follows a modular architecture with clear separation of concerns:

### High-Level Structure

```
roller-installer/
├── pyproject.toml              # Project configuration and dependencies
├── main.py                     # PyInstaller entry point
├── roller_installer/           # Main package
│   ├── __init__.py            
│   ├── __main__.py            # Module entry point (python -m roller_installer)
│   ├── cli/                   # Command-line interface
│   ├── core/                  # Core installer logic
│   ├── utils/                 # Shared utilities
│   ├── gui/                   # GUI interface (planned)
│   └── tui/                   # Terminal UI interface (planned)
├── assets/templates/          # Configuration file templates
├── scripts/                   # Build and utility scripts
└── tests/                     # Test suite
```

### Module Details

#### CLI Layer (`cli/`)
- **`commands.py`** - Complete Typer-based CLI with Rich integration
- Implements all 5 core commands: install, extract-assets, check-updates, list-releases, self-update
- Professional terminal output with progress bars and colored text

#### Core Logic (`core/`)
- **`github_client.py`** - GitHub API integration using PyGithub
- **`ubi_downloader.py`** - UBI integration for platform-specific binary downloads
- **`asset_extractor.py`** - Modular asset extraction system coordinator
- **`handlers/`** - Pluggable asset extraction handlers

#### Utilities (`utils/`)
- **`platform_utils.py`** - Cross-platform path handling and system detection
- **`binary_resolver.py`** - Generic binary resolution with fallback strategies
- **`ubi_resolver.py`** - UBI-specific binary detection and validation
- **`bchunk_resolver.py`** - bchunk binary detection for CUE/BIN support

## Technical Architecture Details

### Asset Extraction System

The installer uses a **modular handler architecture** for extracting FATDATA directories from various formats:

#### Handler Registry Pattern
Handlers are automatically registered by file extension in [`asset_extractor.py`](roller_installer/core/asset_extractor.py). See the existing handlers for examples:
- [`zip_handler.py`](roller_installer/core/handlers/zip_handler.py) 
- [`iso_handler.py`](roller_installer/core/handlers/iso_handler.py)
- [`cue_bin_handler.py`](roller_installer/core/handlers/cue_bin_handler.py)

#### Base Handler Interface
All handlers inherit from `BaseAssetHandler` and must implement:
- `can_handle(file_path)` - Check if handler supports the file
- `extract_fatdata(file_path, output_dir)` - Perform extraction
- `find_fatdata_path(file_path)` - Locate FATDATA within archive

#### Validation and Results
- `ExtractionResult` class provides structured results with validation
- Supports music track extraction from CUE/BIN files
- Includes file count validation and error reporting

#### Supported Formats

**ZIP Handler** (`handlers/zip_handler.py`):
- Case-insensitive FATDATA detection
- Preserves directory structure during extraction
- Handles nested ZIP files

**ISO Handler** (`handlers/iso_handler.py`):
- Uses `pycdlib` for ISO 9660 parsing
- Recursive directory extraction with proper path handling
- Supports Joliet and Rock Ridge extensions

**CUE/BIN Handler** (`handlers/cue_bin_handler.py`):
- Uses `bchunk` for conversion to ISO + separate audio tracks
- Extracts music tracks as individual files
- Handles multi-session discs

### Binary Resolution System

Generic binary resolver with **configurable fallback strategy**:

#### Resolution Order
1. **Local Bundling** - Same directory as installer executable
2. **Project Root** - Development environment detection  
3. **System PATH** - Cross-platform executable detection with proper extensions
4. **Custom Paths** - Configurable additional search locations
5. **Verification** - Test execution to validate working binaries

#### Specialized Resolvers
- **UbiResolver** - Handles UBI installation detection with detailed error messages
- **BchunkResolver** - Manages optional bchunk dependency with graceful fallback

#### Platform Support
See [`binary_resolver.py`](roller_installer/utils/binary_resolver.py) for cross-platform executable detection that handles:
- Windows .exe extensions automatically
- All PATH directory searches  
- Unix execute permission validation

### GitHub Integration

**Complete GitHub API client** with:
- Release management (list, filter by prerelease/stable)
- Asset downloading with progress tracking
- Version comparison and update checking
- Rate limiting and error handling
- Authentication support (for private repos)

### Platform Utilities

**Cross-platform support** including:
- Platform detection and identifier generation (`get_platform_identifier()`)
- Default installation directories with XDG compliance on Linux
- Configuration directory handling
- Administrator/root privilege detection
- Desktop directory resolution for shortcuts

## Implementation Status

### ✅ Completed Features
- **CLI Framework** - Full Typer implementation with Rich output
- **Build System** - PyInstaller native binary generation
- **GitHub Integration** - Complete API client with release management  
- **Binary Downloads** - UBI integration with platform-specific extraction
- **Asset Extraction** - Modular system supporting ZIP, ISO, and CUE/BIN
- **Binary Resolution** - Generic resolver with fallback strategies
- **Version Management** - Installation tracking with `.roller-version` files
- **Platform Support** - Cross-platform utilities and path handling

### 📋 TODO Features
- **Configuration Generation** - FATAL.INI and config.ini template system
- **Installation Management** - Desktop shortcuts and file associations
- **GUI/TUI Interfaces** - Alternative user interfaces beyond CLI
- **Self-Update Logic** - Complete implementation of self-update command

## Contributing Guidelines

### Adding New Asset Handlers

To support a new archive format (e.g., 7z, RAR), create a new handler following the pattern in existing handlers:

1. **Study existing handlers**: Look at [`zip_handler.py`](roller_installer/core/handlers/zip_handler.py), [`iso_handler.py`](roller_installer/core/handlers/iso_handler.py), or [`cue_bin_handler.py`](roller_installer/core/handlers/cue_bin_handler.py)

2. **Create new handler**: Follow the `BaseAssetHandler` interface from [`asset_extractor.py`](roller_installer/core/asset_extractor.py)

3. **Register the handler**: Add your handler to the registry in [`asset_extractor.py`](roller_installer/core/asset_extractor.py) by extending the `_register_default_handlers()` method

**Requirements for new handlers:**
- Must handle case-insensitive FATDATA detection
- Should preserve directory structure during extraction
- Must return proper ExtractionResult with validation
- Include comprehensive error handling
- Add appropriate dependencies to `pyproject.toml`

### Adding New Binary Resolvers

For new external dependencies, create specialized resolvers following the existing pattern:

1. **Study existing resolvers**: Look at [`ubi_resolver.py`](roller_installer/utils/ubi_resolver.py) or [`bchunk_resolver.py`](roller_installer/utils/bchunk_resolver.py)

2. **Use the generic resolver**: Build on [`binary_resolver.py`](roller_installer/utils/binary_resolver.py) using the `BinaryResolver` class and convenience functions

3. **Follow the established pattern**: Create simple wrapper functions that delegate to the generic resolver

### Code Style and Standards

**Linting and Formatting:**
```bash
# Run before committing
ruff check .        # Check for issues
ruff format .       # Auto-format code
```

**Code Standards:**
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions
- Add docstrings for public classes and methods
- Use `pathlib.Path` for all filesystem operations
- Handle errors gracefully with informative messages
- Log important operations using Python's `logging` module

**Error Handling:**
- Use specific exception types rather than generic `Exception`
- Provide clear, actionable error messages to users
- Include context about what operation failed and why
- Use `typer.Exit()` for CLI error conditions


### Building Distributions

#### Single Platform Build
```bash
# Build for current platform
mise run build-installer
# Output: dist/roller-installer (or .exe on Windows)

# Test the built binary
./dist/roller-installer --help
./dist/roller-installer cli install --help
```

#### Cross-Platform Considerations
- **Windows**: Build on Windows for proper `.exe` generation
- **macOS**: Requires macOS for code signing and notarization
- **Linux**: Can build in containers, supports multiple distributions
- **Dependencies**: All Python dependencies are bundled in the binary
- **External Tools**: `ubi` and `bchunk` must be installed separately by users

#### GitHub Actions CI/CD
The project includes GitHub Actions workflows for:
- Automated building for multiple platforms
- Release artifact generation
- Code quality checks with ruff
- Dependency vulnerability scanning

## Development Workflow

### Making Changes

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/ROLLER-installer.git
   cd ROLLER-installer
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-handler
   ```

3. **Make Changes**
   - Follow the architecture patterns described above
   - Update documentation as needed

4. **Test Locally**
   ```bash
   # Run linting
   ruff check .
   ruff format .
   
   # Test from source
   mise run installer -- cli install --help
   
   # Build and test binary
   mise run build-installer
   ./dist/roller-installer cli install --help
   ```

5. **Submit Pull Request**
   - Include clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

### Debugging Tips

**Verbose Output:**
```bash
# Enable verbose logging
roller-installer cli install --verbose

# Debug specific operations
roller-installer cli extract-assets game.iso --verbose
```

**Development Debugging:**
- Add debug logging using Python's `logging` module
- Use breakpoints for step-by-step debugging
- See existing logging patterns in the codebase for examples

**Binary Debugging:**
```bash
# Check what external tools are detected
roller-installer cli list-releases  # Tests GitHub connectivity
roller-installer cli extract-assets --help  # Tests asset extraction setup
```

## Questions and Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Development**: This CONTRIBUTING.md covers most development scenarios

When reporting issues, please include:
- Platform and Python version
- Full command that failed
- Complete error output with `--verbose` flag
- Sample files (if related to asset extraction)

Thank you for contributing to ROLLER Installer!