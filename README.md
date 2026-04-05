# Genetic Similarity Network & Cryptic Relatedness in OpenSNP

Annotate A Genome · Spring 2026

Pairwise IBS analysis across publicly shared genomes from OpenSNP.

## Quick Start

```bash
git clone https://github.com/kmcerr/opensnp_project10.git
cd opensnp_project10
pip install -r requirements.txt

# Place your OpenSNP files under data/ (see data/README.md)

python run_pipeline.py          # run all steps 01 → 07
python run_pipeline.py 7        # start from step 07
python run_pipeline.py 3 6      # run steps 03 through 06
```

**Prerequisites:** Python 3.10+, PLINK 1.9 on your `PATH`.

## Reproducing Results

1. **Same data** — identical `opensnp_Ancestry.csv`, genotype files, and `manifest.csv` under `data/`.
2. **Same tools** — Python 3.10+, packages in `requirements.txt`, PLINK 1.9.
3. **Same thresholds** — don't modify `config.py`.
4. **Same order** — run scripts `01` → `07` sequentially.

The `data/` directory is gitignored except `data/README.md`, which documents required inputs. Raw genotypes and generated outputs are not committed.

## Pipeline

| Script | What It Does |
|--------|-------------|
| `01_create_mapping.py` | Classify 148 unique ancestry strings → tier0/tier1 labels + 16 manual corrections |
| `02_ancestry_grouping.py` | Map all 414 users to ancestry groups |
| `03_data_prep.py` | Audit 405 genotype files, exclude incompatible formats → 329 in pipeline |
| `04_build_verification.py` | Verify genome builds via sentinel SNPs, prepare liftOver for GRCh36 |
| `05_plink_conversion.py` | Convert to PLINK binary → 296 samples |
| `06_merge.py` | Build shared SNP panel (≥90%), merge → 93,476 SNPs |
| `07_qc_ld_ibs.py` | QC (missingness, MAF), LD pruning → 260 samples, 53,131 SNPs; pairwise IBS |

> **Note:** Steps 08–10 (deduplication, visualization, sensitivity analysis) will be added in a future update.

## Project Structure

```
├── README.md                  This file
├── LICENSE                    MIT license text
├── .gitignore
├── config.py                  Central paths, thresholds, constants
├── run_pipeline.py            Run all steps (or a range)
├── requirements.txt
│
├── 01_create_mapping.py       ┐
├── 02_ancestry_grouping.py    │
├── 03_data_prep.py            │
├── 04_build_verification.py   │  Pipeline scripts (run in order)
├── 05_plink_conversion.py     │
├── 06_merge.py                │
├── 07_qc_ld_ibs.py            ┘
│
├── lib/
│   ├── __init__.py
│   ├── parsing.py             Genotype file parsers
│   ├── plink.py               run_plink() subprocess helper
│   ├── ibs.py                 IBS proportions, pair classification, metadata
│   └── network.py             Graph construction and concordance analysis
│
└── data/                      (gitignored except data/README.md)
    ├── README.md              Documents required input files
    ├── opensnp_Ancestry.csv                          ← you provide
    └── opensnp_genotypes_Ancestry__413files/          ← you provide
        ├── manifest.csv
        └── *.txt
```

## Key Thresholds

All defined in `config.py` — change once, applies everywhere.

| Parameter | Value | Script |
|-----------|-------|--------|
| SNP presence | ≥90% of samples | 06 (merge) |
| Sample missingness | >5% removed | 07 (QC) |
| SNP missingness | >5% removed | 07 (QC) |
| MAF | <1% removed | 07 (QC) |
| LD pruning r² | 0.2 | 07 (QC) |

## Outputs

After running the pipeline, `data/` contains:

- `plink_individual/` — one PLINK binary per sample
- `plink_merged/` — merged dataset
- `plink_qc/` — QC-filtered and LD-pruned datasets + IBS results
- `plink_qc/qc_stage_summary.csv` — QC waterfall

## License

MIT
