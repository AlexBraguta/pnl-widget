# 📊 pnl-widget

A lightweight widget that displays your current daily PnL.  
Supports:

- **Arch Linux** via a Waybar module  
- **Ubuntu** via a standalone desktop widget

---

## 🚀 Features

- Real-time daily PnL update  
- Easy Arch/Ubuntu installation  
- Minimal dependencies

---


## 🔧 Prerequisites

- **Common**  
  - Python 3.1+  
  - Always have your daily PnL visible  
- **Arch**  
  - `waybar` installed  
- **Ubuntu**  
  - `python3-pyqt5` or `python3-gi` 

---

## ⚙️ Installation

### Arch Linux (Hyprland with Waybar)

1. Create a simple python env
2. Add waybar conf to your waybar config
3. Point waybar conf to the arch.py file
4. Reload waybar

### Ubuntu (Desktop)

1. Create a simple python env
2. Create a simple shell script for running on launch
3. Point script to the ubuntu.py file
4. Launch

---

## Configuration

Environment variables
```
API_KEY: YOUR_API_KEY
API_SECRET: YOUR_API_SECRET
```

---

## Usage

- **Arch**: your Waybar bar will show `Pnl <amount>` and auto-refresh every 10m.  
- **Ubuntu**: a small window/tray icon shows "Today’s PnL: " and auto-refresh every 10m.

---

## License

MIT License © 2025 Free to use