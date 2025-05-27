# Voice Translator Mobile 🎤🌍📱

[![Android CI/CD](https://github.com/fcozochi/voice-translator-mobile/actions/workflows/android.yml/badge.svg)](https://github.com/fcozochi/voice-translator-mobile/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/fcozochi/voice-translator-mobile/blob/main/LICENSE)

Real-time voice translation app supporting 50+ languages, built with Python/Kivy and deployed to Android.

<div align="center">
  <img src="https://github.com/fcozochi/voice-translator-mobile/blob/main/main.PNG" width="250">
  <img src="https://github.com/fcozochi/voice-translator-mobile/blob/main/translation.PNG" width="250">
</div>

## Features ✨
- Real-time voice recording & translation
- Text-to-speech playback
- Google Cloud API integration
- Auto-built Android APKs via GitHub Actions
- Multi-platform support (Android/Windows/macOS/Linux)

## Installation 📥
### Android (APK)
1. Download latest APK from [Releases](https://github.com/fcozochi/voice-translator-mobile/releases)
2. Enable "Install from unknown sources"
3. Install and launch

### Desktop
```bash
git clone https://github.com/fcozochi/voice-translator-mobile.git
cd voice-translator-mobile
pip install -r requirements.txt
python main.py
