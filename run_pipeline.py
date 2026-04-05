#!/usr/bin/env python3
"""
Run pipeline steps 01 → 07 in order.

Usage:
    python run_pipeline.py              # run all available steps
    python run_pipeline.py 7            # start from step 07
    python run_pipeline.py 3 6          # run steps 03 through 06

Each step's main() is imported and called directly — no subprocesses.
"""

import importlib
import sys
import time

STEPS = [
    ("01", "01_create_mapping",      "Ancestry classification + corrections"),
    ("02", "02_ancestry_grouping",   "Map users to tier0/tier1"),
    ("03", "03_data_prep",           "Audit genotype files + filtering"),
    ("04", "04_build_verification",  "Verify genome builds + liftOver prep"),
    ("05", "05_plink_conversion",    "Convert to PLINK binary"),
    ("06", "06_merge",               "Build shared panel + merge"),
    ("07", "07_qc_ld_ibs",           "QC, LD pruning, pairwise IBS"),
]


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 7

    selected = [(n, mod, desc) for n, mod, desc in STEPS
                if start <= int(n) <= end]

    if not selected:
        print(f"No steps in range {start}–{end}")
        return 1

    from config import DATA_DIR
    print(f"Data directory: {DATA_DIR}")
    print(f"Steps: {selected[0][0]} → {selected[-1][0]}\n")

    for num, module_name, description in selected:
        print("=" * 72)
        print(f"  Step {num}: {description}")
        print("=" * 72)

        try:
            mod = importlib.import_module(module_name)
        except ModuleNotFoundError:
            print(f"  ⚠  {module_name}.py not found — skipping\n")
            continue

        t0 = time.time()
        mod.main()
        elapsed = time.time() - t0
        print(f"\n  Done ({elapsed:.1f}s)\n")

    print("=" * 72)
    print("  Pipeline complete")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
