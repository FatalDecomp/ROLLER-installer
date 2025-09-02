#!/usr/bin/env python3
"""
Standalone entry point for roller-installer.
This file is used for building native binaries.
"""

import sys
from roller_installer.cli.commands import cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
