from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bitcoin options data analytics CLI.",
    )
    parser.add_argument(
        "--iv-surface",
        action="store_true",
        help="render the BTC options implied-volatility surface (Deribit, 3D)",
    )
    args = parser.parse_args()

    if args.iv_surface:
        from volatility import iv_surface

        iv_surface.run()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
