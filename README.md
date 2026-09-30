# Chromatic Studio Bridge

An independent, open-source workflow for building original Game Boy Color games with Codex and getting them onto a ModRetro Chromatic.

The first milestone reuses existing tools:

1. Codex helps create a game project.
2. GB Studio builds a `.gb` or `.gbc` ROM.
3. ChroMagic boots homebrew from the Chromatic's internal microSD card.
4. ChroMagician manages the SD card over USB.
5. PrismGB can show the Chromatic's USB video stream on macOS.

This repository starts with the Codex workflow and a local build/inspection command. Device transfer is a manual ChroMagician step for now. ChroMagician's published installers currently list Windows and Linux, and we need a physical Chromatic to validate the USB transfer protocol and build a reliable macOS bridge.

## What works today

- Codex plugin package with a focused Game Boy Color game-making skill.
- Dependency-free Python command to check for GB Studio CLI, build a ROM, and inspect basic ROM metadata.
- Device setup and transfer guide using ChroMagic and ChroMagician rather than requiring a custom cartridge.

## What is not claimed yet

- One-click transfer from macOS to the Chromatic. The device and transfer flow need testing first.
- Universal game compatibility. ChroMagic SD playback is experimental and excludes some cartridge-peripheral games.
- Official affiliation with OpenAI, ModRetro, Nintendo, or the projects linked below.

## Requirements

- macOS, Windows, or Linux
- Python 3.10+
- GB Studio installed; the `gb-studio-cli` command must be available on `PATH`
- A GB Studio project (`.gbsproj`)

## Quick start

Check the local build setup:

```sh
python3 tools/chromatic.py doctor
```

Build a Game Boy Color ROM:

```sh
python3 tools/chromatic.py build /path/to/MyGame/MyGame.gbsproj
```

The ROM is written to `builds/` by default. Choose another output directory with:

```sh
python3 tools/chromatic.py build /path/to/MyGame/MyGame.gbsproj --out /path/to/output
```

Inspect an existing ROM:

```sh
python3 tools/chromatic.py inspect builds/MyGame.gbc
```

### Play one game from another creator

The official [ModRetro + OpenAI game showcase](https://developers.openai.com/modretro) lists games with browser play and, for games that provide it, a downloadable ROM. Download a game individually from its creator's page, then import that local file into your private library:

```sh
python3 tools/chromatic.py library import ~/Downloads/ExampleGame.gbc \\
  --title "Example Game" \\
  --source "https://example.com/game" \\
  --rights "Use permitted by the creator's listed terms"
python3 tools/chromatic.py library list
```

The library records the source, rights note, and SHA-256 checksum. ROM files and the library catalog live in `local-library/`, which Git ignores so other creators' games are not accidentally committed or published with this project. Check each creator's terms before downloading or using a ROM; the project does not host or redistribute games.

For device play, use ChroMagician to copy the selected individual ROM from `local-library/roms/` to the Chromatic SD card, then launch it from ChroMagic's Backups view. This is a manual handoff in the first version: the exact SD path and direct transfer automation still need validation on a physical Chromatic. ChroMagic SD playback is experimental, so some games may not run.

The project can make that flow smoother as the device and host OS are tested: a browse/import catalog, compatibility notes, then a transfer adapter using a supported ChroMagician interface. The public GitHub project should contain the pipeline and metadata format, never third-party ROM binaries.

The build command uses GB Studio's documented `make:rom` CLI operation. This helper does not replace the GB Studio editor or its preview.

## Codex plugin

The repository includes a portable Codex plugin at `.agents/plugins/chromatic-studio/`. To try it from a local checkout, add `./.agents/plugins` as a local plugin marketplace in Codex, then install **Chromatic Studio Bridge**. Keep game projects inside this checkout (for example, under `games/`) so the helper command is available. Invoke its `chromatic-game-workflow` skill and point Codex at the `.gbsproj` to build.

The skill asks Codex to use the existing GB Studio toolchain and this repository's helper. It does not claim to control a connected Chromatic yet.

## Device workflow: manual first prototype

1. Confirm the Chromatic revision has an internal microSD socket. ChroMagic's guide says 2025-and-later models have one fitted; most first-edition units do not.
2. Follow the ChroMagic installation guide and install its companion app. Keep the stock firmware available; ChroMagician documents restoring stock firmware.
3. Build an original `.gb` or `.gbc` game with this project.
4. Use ChroMagician to copy the ROM to the Chromatic's SD card. ChroMagic describes SD playback as experimental.
5. On the Chromatic, open the Backups tab and launch the game.
6. For real-device video on a Mac, try PrismGB over USB.

Never interrupt a firmware write. Back up a game/save before rewriting a cartridge. This project only targets original homebrew and does not provide game ROMs.

## Roadmap

- [x] Codex workflow package and GB Studio build helper
- [x] ROM metadata inspection and build output organization
- [x] Private local library for individually imported and attributed ROMs
- [ ] Validate the workflow on an actual Chromatic and record its revision
- [ ] Test ChroMagic SD playback with a known-good original homebrew ROM
- [ ] Determine the easiest supported macOS transfer path
- [ ] Add an optional transfer command once the path is verified
- [ ] Add emulator launch/automated playtest integration after choosing a maintained emulator interface
- [ ] Publish a release and installation instructions for the Codex plugin

## Existing projects this builds on

- [GB Studio](https://github.com/chrismaltby/gb-studio) — editor and ROM build toolchain (MIT).
- [ChroMagician](https://github.com/cursedtoast2/ChroMagician) — community USB companion for ChroMagic (GPL-3.0).
- [ChroMagic guide](https://chromagic.org/guide) — community firmware install, SD setup, playback, and compatibility details.
- [PrismGB](https://github.com/josstei/prismgb-app) — community Chromatic USB video/capture application (MIT).
- [ModRetro Chromatic FPGA source](https://github.com/ModRetro/oss-chromatic-console-fpga) and [MCU source](https://github.com/ModRetro/oss-chromatic-console-mcu) — official hardware firmware source; not needed for the first ROM pipeline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). For device issues, include host OS, device revision, firmware version, ROM build method, and exact reproduction steps. Do not include copyrighted ROMs or save files in bug reports.

## License and naming

The code in this repository is MIT-licensed. Third-party projects retain their own licenses. “Chromatic” and “ModRetro” describe compatibility only; this is an independent community project, not endorsed by ModRetro or OpenAI.
