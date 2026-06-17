import argparse
import sys
from pathlib import Path

from container2nft.convert import convert


def main():
    parser = argparse.ArgumentParser(
        description="Convert container configuration to nftables rules"
    )
    parser.add_argument("config", help="containers.toml")
    parser.add_argument("output", help="output directory")
    parser.add_argument("table", type=str, help="nftables table name")
    args = parser.parse_args()

    cfg_path = Path(args.config).resolve()
    out_root = Path(args.output).resolve()

    if not cfg_path.exists():
        parser.error(f"config file does not exist: {cfg_path}")

    if not cfg_path.is_file():
        parser.error(f"config path is not a file: {cfg_path}")

    if not out_root.is_dir():
        parser.error(f"output path is not a directory: {out_root}")

    try:
        convert(cfg_path, out_root)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
