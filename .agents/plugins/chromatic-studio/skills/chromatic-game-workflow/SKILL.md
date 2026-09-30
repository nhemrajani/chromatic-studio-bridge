---
name: chromatic-game-workflow
description: Create, edit, build, and prepare original Game Boy or Game Boy Color homebrew projects for testing on a ModRetro Chromatic. Use when the user wants to make a handheld game, build a GB/GBC ROM, or prepare a ROM for a Chromatic.
---

# Chromatic game workflow

Use this workflow for original games only. Do not fetch, reproduce, or distribute commercial ROMs or copyrighted game assets.

## Workflow

1. Identify the target project and whether it is a GB Studio project (`.gbsproj`) or another compatible source project. Do not overwrite an unrelated project.
2. If the user has an idea but no project, create a new GB Studio project in a location the user specifies. Keep the game's scope small and use assets the user created, supplied, or has permission to use.
3. Respect Game Boy / Game Boy Color hardware limits and GB Studio warnings. Prefer project-native edits through GB Studio where practical.
4. Build from the project root with `python3 tools/chromatic.py build /path/to/project.gbsproj`, when this repository is available in the current workspace. Otherwise use the installed `gb-studio-cli` `make:rom` command.
5. Inspect the output with `python3 tools/chromatic.py inspect /path/to/game.gb[c]`. Report the output path and any header warnings.
6. Open the project in GB Studio or its supported preview to playtest. Do not claim a game passed an emulator or hardware test unless that test was actually performed.
7. For an individually downloaded third-party homebrew ROM, require a creator/page source and use `python3 tools/chromatic.py library import <file.gb[c]> --title "..." --source "..." --rights "..."` to keep an attributed local copy. Use `python3 tools/chromatic.py library list` to review the library. Never put ROM files in Git or upload them to this project's public repository.
8. For a physical Chromatic, explain that transfer is currently manual: install ChroMagic, use ChroMagician to copy the selected ROM from `local-library/roms/` to the internal SD card, then launch it from the device's Backups tab. ChroMagic SD playback is experimental. Do not claim this plugin itself transferred or launched the ROM.

## Safety and accuracy

- Ask before replacing an existing game cartridge or overwriting an existing output file.
- Never automatically flash firmware or a cartridge.
- Never claim retail developer-mode activation is available.
- Be clear that this is an independent project, not an official OpenAI or ModRetro product.
