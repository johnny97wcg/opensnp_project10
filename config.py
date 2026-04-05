"""
Project 10 — Central Configuration
===================================
All paths, thresholds, and constants live here.
Every pipeline script imports from this module.

Path resolution (no hardcoded paths):
  1. If PROJECT10_DATA_DIR is set, use that for data.
  2. Otherwise, use <repo_root>/data/

To run on your machine:
  1. Clone the repo.
  2. Place your OpenSNP files under data/ (see data/README.md).
  3. Run scripts 01 → 07 in order (see run_pipeline.py).
"""

import os
from pathlib import Path


def _find_repo_root() -> Path:
    """Walk up from this file to find the repo root (contains lib/)."""
    p = Path(__file__).resolve().parent
    # config.py is at repo root
    if (p / "lib").is_dir():
        return p
    # config.py might be inside lib/ or original_scripts/
    if (p.parent / "lib").is_dir():
        return p.parent
    return p


# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════

PROJECT_DIR = Path(
    os.environ.get("PROJECT10_PROJECT_DIR", str(_find_repo_root()))
).resolve()

DATA_DIR = Path(
    os.environ.get("PROJECT10_DATA_DIR", str(PROJECT_DIR / "data"))
).resolve()

RAW_GENO_DIR = DATA_DIR / "opensnp_genotypes_Ancestry__413files"

# ── Input files ──
RAW_ANCESTRY_CSV = DATA_DIR / "opensnp_Ancestry.csv"
MANIFEST_CSV = RAW_GENO_DIR / "manifest.csv"

# ── Ancestry mapping ──
MAPPING_CSV = DATA_DIR / "opensnp_Ancestry_unique_mapping_final_v4.csv"
GROUPINGS_CSV = DATA_DIR / "opensnp_Ancestry_final_groupings_v4.csv"

# ── Pipeline intermediates ──
MASTER_MANIFEST_CSV = DATA_DIR / "master_manifest.csv"
AUDIT_RESULTS_CSV = DATA_DIR / "audit_results_revised.csv"
PIPELINE_MANIFEST_CSV = DATA_DIR / "pipeline_manifest_revised.csv"
CONVERSION_READY_CSV = DATA_DIR / "conversion_ready_manifest.csv"
STAGE4_INPUT_CSV = DATA_DIR / "stage4_input_manifest.csv"

# ── Directories ──
PLINK_INDIVIDUAL_DIR = DATA_DIR / "plink_individual"
MERGE_DIR = DATA_DIR / "plink_merged" / "full_merge" / "strict_retry"
FILTERED_DIR = MERGE_DIR / "filtered_inputs"
QC_DIR = DATA_DIR / "plink_qc"
NETWORK_DIR = DATA_DIR / "network_analysis"
DEDUP_DIR = DATA_DIR / "deduplicated_analysis"
SENSITIVITY_DIR = DATA_DIR / "sensitivity_eur_only"
LIFTOVER_DIR = DATA_DIR / "liftover"
FIG_DIR = DATA_DIR / "figures"

# ── Merged dataset ──
MERGED_PREFIX = MERGE_DIR / "full_merged_strict"

# ── QC step prefixes ──
QC_MISSING_PREFIX = QC_DIR / "qc_missingness"
QC_STEP1_PREFIX = QC_DIR / "step1_sample_filtered"
QC_STEP2_PREFIX = QC_DIR / "step2_snp_filtered"
QC_STEP3_PREFIX = QC_DIR / "step3_maf_filtered"
QC_STEP3B_PREFIX = QC_DIR / "step3b_no_ambiguous"
QC_LD_PRUNE_PREFIX = QC_DIR / "step4_ld_prune"
QC_PRUNED_PREFIX = QC_DIR / "step4_pruned_dataset"
QC_IBS_PREFIX = QC_DIR / "step5_ibs"

# ── Dedup prefixes ──
DEDUP_PREFIX = DEDUP_DIR / "step1_pruned_deduplicated"
DEDUP_IBS_PREFIX = DEDUP_DIR / "step2_ibs_deduplicated"

# ── liftOver ──
LIFTOVER_BED_DIR = LIFTOVER_DIR / "bed_inputs"
LIFTOVER_OUT_DIR = LIFTOVER_DIR / "lifted_bed"
LIFTOVER_UNMAPPED_DIR = LIFTOVER_DIR / "unmapped"
CHAIN_FILE = LIFTOVER_DIR / "hg18ToHg19.over.chain.gz"
LIFTOVER_EXEC = "liftOver"


# ═══════════════════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════════════════

PLINK_EXEC = os.environ.get("PLINK_EXEC", "plink")
N_THREADS = int(os.environ.get("PROJECT10_THREADS", "4"))


# ═══════════════════════════════════════════════════════════════════
# THRESHOLDS
# ═══════════════════════════════════════════════════════════════════

# ── Merge ──
SNP_PRESENCE_THRESHOLD = 0.90
MERGE_MAX_ATTEMPTS = 3

# ── Conversion ──
MIN_PARSED_SNPS = 10_000

# ── QC ──
SAMPLE_MISS_THRESHOLD = 0.05
SNP_MISS_THRESHOLD = 0.05
MAF_THRESHOLD = 0.01
LD_WINDOW = 50
LD_STEP = 5
LD_R2 = 0.2

# ── Relatedness ──
IBS2_PRUNE_THRESHOLD = 0.1
IBS2_RELATEDNESS_THRESHOLD = 0.4
PIHAT_3RD_DEGREE = 0.125
PIHAT_2ND_DEGREE = 0.25
PIHAT_1ST_DEGREE = 0.4
PIHAT_DUPLICATE = 0.9

# ── Network ──
PIHAT_EDGE_THRESHOLD = 0.05


# ═══════════════════════════════════════════════════════════════════
# CONTROLLED VOCABULARIES
# ═══════════════════════════════════════════════════════════════════

EXPECTED_TIER0 = {"EUR", "Non-EUR", "Admixed", "Founder", "Unknown"}

TIER0_ORDER = ["EUR", "Non-EUR", "Admixed", "Founder", "Unknown"]

TIER0_COLORS = {
    "EUR":     "#4C72B0",
    "Non-EUR": "#DD8452",
    "Admixed": "#55A868",
    "Founder": "#C44E52",
    "Unknown": "#8C8C8C",
}

AUTOSOMAL_CHROMS = {str(i) for i in range(1, 23)}

VALID_BASES = {"A", "C", "G", "T"}

SENTINELS = {
    "rs3131972":  {"chr": "1", "GRCh37": 752721, "GRCh36": 742429},
    "rs12562034": {"chr": "1", "GRCh37": 768448, "GRCh36": 758156},
    "rs9442372":  {"chr": "1", "GRCh37": 54490,  "GRCh36": 45498},
}


# ═══════════════════════════════════════════════════════════════════
# DIRECTORY CREATION
# ═══════════════════════════════════════════════════════════════════

def ensure_dirs():
    """Create all output directories. Safe to call multiple times."""
    for d in [
        PLINK_INDIVIDUAL_DIR, MERGE_DIR, FILTERED_DIR,
        QC_DIR, NETWORK_DIR, DEDUP_DIR, SENSITIVITY_DIR,
        LIFTOVER_DIR, LIFTOVER_BED_DIR, LIFTOVER_OUT_DIR,
        LIFTOVER_UNMAPPED_DIR, FIG_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)
