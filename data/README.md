# Data Directory

This directory is where the pipeline reads inputs from and writes outputs to. **Nothing under `data/` is committed to git** except this README — users provide their own copies of the raw OpenSNP files.

## Required inputs

Place these files here before running the pipeline:

| Path | Description |
|------|-------------|
| `opensnp_Ancestry.csv` | Self-reported ancestry strings (414 rows, from the class OpenSNP browser) |
| `opensnp_genotypes_Ancestry__413files/manifest.csv` | Lists genotype filenames for each user |
| `opensnp_genotypes_Ancestry__413files/*.txt` | Raw genotype files (23andMe / AncestryDNA format) |

Optional: `liftover/hg18ToHg19.over.chain.gz` if you have GRCh36 files that need coordinate lifting (step 04).

## Generated outputs

Running `01_create_mapping.py` through `07_qc_ld_ibs.py` populates this directory with intermediate CSVs, PLINK datasets, and IBS results. Key output subdirectories:

- `plink_individual/` — one PLINK binary per sample
- `plink_merged/` — merged dataset
- `plink_qc/` — QC-filtered and LD-pruned datasets + IBS results

## Alternative data location

To keep raw data elsewhere (e.g., an external drive), set the environment variable before running:

```bash
export PROJECT10_DATA_DIR=/path/to/your/data
python run_pipeline.py
```
