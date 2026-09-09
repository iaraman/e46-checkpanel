# E46 Check Panel

Retrofit E30-style check control panel for the BMW E46, driven by live PT-CAN data on an ESP32.

## Layout
| Folder | What lives here |
|---|---|
| `docs/` | Human-readable knowledge: decisions, CAN map, learning log |
| `tools/` | Python scripts that run on your computer (decode logs, bench testing) |
| `sample_data/` | CAN logs (synthetic now, real captures later) |
| `firmware/` | ESP32 code (PlatformIO project, Phase 3) |
| `scripts/` | One-shot setup scripts for macOS and Windows |
| `CLAUDE.md` | Instructions Claude Code reads every session — the project's memory |

## First-time setup
macOS: `bash scripts/setup-mac.sh`   Windows (PowerShell): `.\scripts\setup-windows.ps1`

Then open this folder in VS Code and accept the recommended extensions.
