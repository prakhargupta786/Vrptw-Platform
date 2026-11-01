"""python -m vrptw_core.cli generate --seed 20261022 --scale full --out storage/runs/local
   python -m vrptw_core.cli reproduce --seed 20261022 --scale starter"""
import argparse

from vrptw_core.config import RunConfig


def main() -> None:
    ap = argparse.ArgumentParser(prog="vrptw")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("generate", "validate", "reproduce"):
        p = sub.add_parser(name)
        p.add_argument("--seed", type=int, default=20261022)
        p.add_argument("--scale", choices=["starter", "full"], default="full")
        p.add_argument("--out", default="storage/runs/local")
    args = ap.parse_args()
    cfg = RunConfig(seed=args.seed) if args.scale == "full" else RunConfig.starter(args.seed)
    print(f"{args.cmd}: {cfg}")
    raise NotImplementedError(args.cmd)


if __name__ == "__main__":
    main()
