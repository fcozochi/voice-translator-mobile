#!/bin/bash
# WSL -> Windows sync
rsync -avz --delete ~/projects/voice-translator-mobile/ /mnt/e/voice-translator-mobile/ --exclude='.venv' --exclude='.buildozer'
