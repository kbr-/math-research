#!/usr/bin/env python3
"""Run the compiled span kernel on a list of instances and collect its JSON lines.

Orchestration only: every instance is one call of the kernel binary; results are appended to
the output file as each case finishes, so a timeout keeps the finished cases.
Usage: run_series.py --kernel BIN --dir INSTANCE_DIR --out OUT.jsonl --cases n:seed:maxD,...
"""
import argparse
import json
import subprocess
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", required=True)
    args = ap.parse_args()
    with open(args.out, "a") as out:
        for case in args.cases.split(","):
            n, seed, maxd = case.split(":")
            t0 = time.time()
            res = subprocess.run([args.kernel, f"{args.dir}/inst_n{n}_s{seed}.txt", maxd],
                                 capture_output=True, text=True, check=True)
            rec = json.loads(res.stdout.strip().splitlines()[-1])
            rec.update({"seed": int(seed), "max_degree": int(maxd), "seconds": round(time.time() - t0, 2)})
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
