#!/usr/bin/env python3
"""
Analyze PyInstaller build log to understand what's included in the binary.
"""

import re
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple


def read_build_log() -> List[str]:
    """Read the build log file."""
    log_file = Path("build.log")
    if not log_file.exists():
        print(
            "❌ No build.log found. Run 'mise run build:verbose' first to generate a build log."
        )
        sys.exit(1)

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()


def extract_included_modules(lines: List[str]) -> List[str]:
    """Extract modules being included."""
    modules = []
    for line in lines:
        if "INFO: Including module" in line:
            match = re.search(r"Including module ([^\s]+)", line)
            if match:
                modules.append(match.group(1))
    return sorted(set(modules))


def extract_processed_modules(lines: List[str]) -> List[str]:
    """Extract packages being processed."""
    packages = []
    for line in lines:
        if "INFO: Processing module" in line and ("from" in line or "package" in line):
            match = re.search(r"Processing module ([^\s]+)", line)
            if match:
                package = match.group(1).split()[0]
                packages.append(package)
    return sorted(set(packages))


def extract_hidden_imports(lines: List[str]) -> List[str]:
    """Extract hidden imports found."""
    hidden = []
    for line in lines:
        if "Hidden import" in line:
            match = re.search(r"Hidden import ['\"](.*?)['\"]", line)
            if match:
                hidden.append(match.group(1))
    return sorted(set(hidden))


def extract_package_frequencies(lines: List[str]) -> List[Tuple[str, int]]:
    """Extract package frequencies."""
    packages = []
    for line in lines:
        if "INFO: Processing" in line or "INFO: Including" in line:
            # Extract package names (module.submodule pattern)
            matches = re.findall(r"\b([a-z_]+\.[a-z_]+)\b", line.lower())
            packages.extend(matches)

    counter = Counter(packages)
    return counter.most_common(15)


def get_binary_size() -> str:
    """Get the size of the built binary."""
    for pattern in ["dist/roller-installer.exe", "dist/roller-installer"]:
        binary = Path(pattern)
        if binary.exists():
            size_mb = binary.stat().st_size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
    return "Binary not found"


def main():
    """Main analysis function."""
    print("🔍 Analyzing PyInstaller Build Log\n")

    lines = read_build_log()

    # Modules being included
    print("=== Modules Being Included (Top 20) ===")
    modules = extract_included_modules(lines)
    for i, module in enumerate(modules[:20], 1):
        print(f"  {i:2}. {module}")
    if len(modules) > 20:
        print(f"  ... and {len(modules) - 20} more modules")

    # Packages being processed
    print("\n=== Packages Being Processed (Top 20) ===")
    packages = extract_processed_modules(lines)
    for i, package in enumerate(packages[:20], 1):
        print(f"  {i:2}. {package}")
    if len(packages) > 20:
        print(f"  ... and {len(packages) - 20} more packages")

    # Hidden imports
    print("\n=== Hidden Imports Found ===")
    hidden = extract_hidden_imports(lines)
    if hidden:
        for i, imp in enumerate(hidden[:10], 1):
            print(f"  {i:2}. {imp}")
        if len(hidden) > 10:
            print(f"  ... and {len(hidden) - 10} more hidden imports")
    else:
        print("  No hidden imports found")

    # Binary size
    print("\n=== Binary Size Analysis ===")
    size = get_binary_size()
    print(f"  Final binary size: {size}")

    # Top included packages by frequency
    print("\n=== Top Included Packages by Frequency ===")
    frequencies = extract_package_frequencies(lines)
    for i, (package, count) in enumerate(frequencies, 1):
        print(f"  {i:2}. {package}: {count} references")

    # Summary statistics
    print("\n=== Summary Statistics ===")
    print(f"  Total modules included: {len(modules)}")
    print(f"  Total packages processed: {len(packages)}")
    print(f"  Total hidden imports: {len(hidden)}")
    print(f"  Total log lines analyzed: {len(lines)}")

    # Look for potential optimization opportunities
    print("\n=== Optimization Opportunities ===")

    # Check for large packages that might be excludable
    large_packages = [
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "PIL",
        "cv2",
        "tensorflow",
        "torch",
        "sklearn",
        "django",
        "flask",
    ]
    found_large = [pkg for pkg in large_packages if any(pkg in m for m in modules)]
    if found_large:
        print("  ⚠️  Large packages detected that might be excludable:")
        for pkg in found_large:
            print(f"     - {pkg}")
    else:
        print("  ✅ No obvious large packages detected")

    # Check for test modules
    test_modules = [m for m in modules if "test" in m.lower() or "pytest" in m.lower()]
    if test_modules:
        print(
            f"  ⚠️  Found {len(test_modules)} test-related modules that could be excluded"
        )
        for module in test_modules[:3]:
            print(f"     - {module}")
    else:
        print("  ✅ No test modules detected")

    print("\n✨ Analysis complete!")


if __name__ == "__main__":
    main()
