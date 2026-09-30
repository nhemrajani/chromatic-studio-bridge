#!/usr/bin/env python3
"""Small GB Studio build and ROM inspection helper for Chromatic homebrew."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def doctor(_args: argparse.Namespace) -> int:
    print(f"Python: {sys.version.split()[0]}")
    cli = shutil.which("gb-studio-cli")
    if cli:
        print(f"GB Studio CLI: {cli}")
        return 0
    print("GB Studio CLI: not found on PATH")
    print("Install GB Studio and make gb-studio-cli available, or consult GB Studio's CLI documentation.")
    return 1


def header_checksum(rom: bytes) -> tuple[int, int] | None:
    if len(rom) < 0x150:
        return None
    computed = 0
    for byte in rom[0x134:0x14D]:
        computed = (computed - byte - 1) & 0xFF
    return computed, rom[0x14D]


def inspect_rom(path: Path) -> int:
    if not path.is_file():
        print(f"ROM not found: {path}", file=sys.stderr)
        return 2
    rom = path.read_bytes()
    if path.suffix.lower() not in {".gb", ".gbc"}:
        print("Warning: expected a .gb or .gbc file")
    if len(rom) < 0x150:
        print(f"Invalid ROM: {len(rom)} bytes; the cartridge header is incomplete", file=sys.stderr)
        return 2

    cgb_flag = rom[0x143]
    title = rom[0x134:0x143].split(b"\0", 1)[0].decode("ascii", errors="replace").strip()
    cart_type = rom[0x147]
    rom_size = rom[0x148]
    checksum = header_checksum(rom)
    nintendo_logo = bytes.fromhex(
        "CEED6666CC0D000B03730083000C000D0008111F8889000EDCCC6EE6DDDDD999"
        "BBBB67636E0EECCCDDDC999FBBB9333E"
    )
    logo_ok = rom[0x104:0x134] == nintendo_logo

    print(f"File: {path.resolve()}")
    print(f"Size: {len(rom):,} bytes")
    print(f"Title: {title or '(untitled)'}")
    print(f"Color support flag: 0x{cgb_flag:02X}")
    print(f"Cartridge type code: 0x{cart_type:02X}")
    print(f"ROM size code: 0x{rom_size:02X}")
    if checksum:
        result = "OK" if checksum[0] == checksum[1] else f"mismatch (computed 0x{checksum[0]:02X})"
        print(f"Header checksum: {result}")
    if not logo_ok:
        print("Warning: Nintendo logo bytes differ from the standard header; some hardware/boot paths may reject this ROM.")
    return 0


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "game"


def library_import(args: argparse.Namespace) -> int:
    source = args.rom.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in {".gb", ".gbc"}:
        print("Choose an existing .gb or .gbc ROM file.", file=sys.stderr)
        return 2
    if inspect_rom(source) != 0:
        return 2

    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    root = args.library.expanduser().resolve()
    rom_dir = root / "roms"
    rom_dir.mkdir(parents=True, exist_ok=True)
    destination = rom_dir / f"{digest[:12]}-{slugify(args.title)}{source.suffix.lower()}"
    if not destination.exists():
        shutil.copy2(source, destination)

    catalog_path = root / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else []
        if not isinstance(catalog, list):
            raise ValueError("catalog must contain a JSON list")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Could not read {catalog_path}: {error}", file=sys.stderr)
        return 2

    entry = {
        "title": args.title,
        "file": str(destination.relative_to(root)),
        "sha256": digest,
        "source": args.source,
        "license_or_permission": args.rights or "Not recorded; verify the creator's terms",
    }
    catalog = [item for item in catalog if item.get("sha256") != digest]
    catalog.append(entry)
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Imported: {args.title}\nROM: {destination}\nCatalog: {catalog_path}")
    print("This is a local copy. Do not upload or redistribute it unless the creator's license permits that.")
    return 0


def library_list(args: argparse.Namespace) -> int:
    catalog_path = args.library.expanduser().resolve() / "catalog.json"
    if not catalog_path.exists():
        print("Game library is empty. Import a ROM with `library import`.")
        return 0
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read {catalog_path}: {error}", file=sys.stderr)
        return 2
    for item in catalog:
        print(f"{item['title']}  [{item['file']}]\n  Source: {item['source']}\n  Rights: {item['license_or_permission']}\n  SHA-256: {item['sha256']}")
    return 0


def build(args: argparse.Namespace) -> int:
    project = args.project.expanduser().resolve()
    if not project.is_file() or project.suffix.lower() != ".gbsproj":
        print(f"Expected an existing GB Studio .gbsproj file: {project}", file=sys.stderr)
        return 2
    cli = shutil.which(args.cli)
    if not cli:
        print(f"GB Studio CLI not found: {args.cli}. Run `python3 tools/chromatic.py doctor`.", file=sys.stderr)
        return 2

    out_dir = args.out.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{project.stem}.{args.format}"
    if output.exists() and not args.force:
        print(f"Output already exists: {output}\nChoose another --out directory or pass --force to replace it.", file=sys.stderr)
        return 2

    command = [cli, "make:rom", str(project), str(output)]
    print("Building with GB Studio:", " ".join(command))
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        return result.returncode
    if not output.is_file():
        print(f"GB Studio returned success but the expected file was not created: {output}", file=sys.stderr)
        return 1
    print("\nROM inspection:")
    return inspect_rom(output)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Build and inspect original GB/GBC ROMs for Chromatic testing.")
    commands = root.add_subparsers(dest="command", required=True)

    check = commands.add_parser("doctor", help="Check the local Python and GB Studio CLI setup")
    check.set_defaults(func=doctor)

    build_cmd = commands.add_parser("build", help="Build a ROM from a GB Studio project")
    build_cmd.add_argument("project", type=Path, help="Path to a .gbsproj file")
    build_cmd.add_argument("--out", type=Path, default=Path("builds"), help="Output directory (default: ./builds)")
    build_cmd.add_argument("--format", choices=("gbc", "gb"), default="gbc", help="Output extension (default: gbc)")
    build_cmd.add_argument("--cli", default="gb-studio-cli", help="GB Studio CLI executable")
    build_cmd.add_argument("--force", action="store_true", help="Replace an existing output ROM")
    build_cmd.set_defaults(func=build)

    inspect_cmd = commands.add_parser("inspect", help="Print basic metadata from a GB/GBC ROM")
    inspect_cmd.add_argument("rom", type=Path)
    inspect_cmd.set_defaults(func=lambda args: inspect_rom(args.rom.expanduser().resolve()))

    library_cmd = commands.add_parser("library", help="Keep an attributed local library of individual game ROMs")
    library_sub = library_cmd.add_subparsers(dest="library_command", required=True)
    import_cmd = library_sub.add_parser("import", help="Import one locally downloaded GB/GBC ROM")
    import_cmd.add_argument("rom", type=Path)
    import_cmd.add_argument("--title", required=True, help="Game title shown in your local catalog")
    import_cmd.add_argument("--source", required=True, help="Creator or page where you obtained the ROM")
    import_cmd.add_argument("--rights", help="License or permission note from the creator")
    import_cmd.add_argument("--library", type=Path, default=Path("local-library"), help="Local library directory (default: ./local-library)")
    import_cmd.set_defaults(func=library_import)
    list_cmd = library_sub.add_parser("list", help="List locally imported games and their source notes")
    list_cmd.add_argument("--library", type=Path, default=Path("local-library"))
    list_cmd.set_defaults(func=library_list)
    return root


if __name__ == "__main__":
    args = parser().parse_args()
    raise SystemExit(args.func(args))
