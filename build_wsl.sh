#!/bin/bash
# Prevent root detection issues
export HOME=/home/$USER  # Force user home directory
unset SUDO_UID SUDO_GID  # Remove sudo environment traces
buildozer "$@"