import re
import pandas as pd

from config import RAW_ANCESTRY_CSV, MAPPING_CSV

KW_EUR_NW = [
    "british", "english", "irish", "welsh", "scottish", "scotland",
    "northern european", "north european", "northwestern european",
    "northwest european", "nw european", "scandinavian", "scandinavia",
    "scandavia", "swedish", "norwegian", "norweig", "danish", "dutch",
    "anglo", "celtic", "viking", "huguenot", "frisian",
    "french", "orcadian",
]

KW_EUR_S = [
    "south european", "southern european", "mediterranean",
    "italian", "iberian", "iberia", "maltese", "balkan",
    "sardinian", "portugese", "portuguese", "spanish", "greek", "romanian",
]

KW_EUR_E = [
    "eastern european", "east european", "north eastern european",
    "ukrainian", "ukranian", "polish", "latvian", "baltic",
    "slavic", "slovak", "sorbian", "czech", "hungarian",
    "finnish", "finn", "russian",
]

KW_EUR_C = [
    "german", "swiss", "austrian", "central european", "frankish", "bavaria",
]

KW_EUR_GENERAL = ["european", "europe"]

KW_AFRICAN = ["african", "sub-saharan", "west african"]

KW_EAST_ASIAN = [
    "east asian", "chinese", "korean", "japanese", "vietnamese",
    "siberian", "southeast asian",
    "asia",
]

KW_SOUTH_ASIAN = ["south asian", "sri lankan", "pashtun"]

KW_MIDDLE_EASTERN = [
    "middle eastern", "m. eastern", "arab", "iranian",
    "algerian", "western asian", "asia minor", "western asia",
]

KW_AMERICAS = [
    "native american", "amerindian", "leni lenape",
    "southern american", "panamanian",
]

KW_OCEANIAN = ["melanesia", "melanesian", "austronesian"]

KW_JEWISH = ["ashkenazi", "sephardic", "jewish", "levite"]

HAPLOGROUP_RE = re.compile(r"^[A-Z]\d|^[A-Z]-[A-Z]", re.IGNORECASE)
SOCIAL_LABELS = {"caucasian"}
VAGUE_LABELS = {"mixed", "mixed ancestry"}


def has_any(tl, kws):
    return any(kw in tl for kw in kws)


def classify(raw_ancestry):
    text = raw_ancestry.strip()
    tl = text.lower()

    # ── Special cases ──
    if HAPLOGROUP_RE.match(text) and not has_any(tl, ["european", "african", "asian"]):
        return "Unknown", "Haplogroup", "Y-DNA or mtDNA haplogroup, not a population"
    if tl in SOCIAL_LABELS:
        return "Unknown", "Social_label", "Social label, not a genetic population"
    if tl in VAGUE_LABELS:
        return "Unknown", "Vague_mixed", "Too vague to assign a population"
    if tl == "viking & celtic":
        return "Unknown", "Other_unknown", "Historical/cultural labels"

    # ── Detect components ──
    has_nw = has_any(tl, KW_EUR_NW)
    has_s = has_any(tl, KW_EUR_S)
    has_e = has_any(tl, KW_EUR_E)
    has_c = has_any(tl, KW_EUR_C)
    has_gen = has_any(tl, KW_EUR_GENERAL)
    has_eur = has_nw or has_s or has_e or has_c or has_gen

    has_sas = has_any(tl, KW_SOUTH_ASIAN)
    has_me = has_any(tl, KW_MIDDLE_EASTERN)
    has_afr = has_any(tl, KW_AFRICAN)
    has_oce = has_any(tl, KW_OCEANIAN)
    has_amr = has_any(tl, KW_AMERICAS)
    has_eas = has_any(tl, KW_EAST_ASIAN) and not has_sas and not has_me
    if "asian" in tl and has_eur and not has_eas and not has_sas:
        has_eas = True

    has_jew = has_any(tl, KW_JEWISH)
    has_mex = "mexican" in tl

    non_eur = []
    if has_afr: non_eur.append("AFR")
    if has_eas: non_eur.append("EAS")
    if has_sas: non_eur.append("SAS")
    if has_me: non_eur.append("ME")
    if has_amr: non_eur.append("AMR")
    if has_oce: non_eur.append("OCE")

    # ── Pure non-EUR ──
    if not has_eur and not has_jew and not has_mex:
        nm = {"AFR": "AFR", "EAS": "EAS", "SAS": "SAS",
              "ME": "MENA", "AMR": "AMR", "OCE": "Other"}
        if len(non_eur) == 1:
            t1 = nm.get(non_eur[0], "Other")
            return "Non-EUR", t1, f"Non-European: {non_eur[0]}"
        if len(non_eur) == 0 and has_any(tl, KW_EAST_ASIAN):
            return "Non-EUR", "EAS", "East Asian"

    # ── Founder ──
    if has_jew and not has_mex:
        if not has_eur and len(non_eur) == 0:
            if "sephardic" in tl and "ashkenazi" in tl:
                return "Founder", "Sephardic", "Ashkenazi + Sephardic Jewish"
            if "ashkenazi" in tl:
                return "Founder", "Ashkenazi", "Ashkenazi Jewish"
            return "Founder", "Founder_mixed", "Jewish label"
        if has_eur and len(non_eur) == 0:
            if "quarter" in tl or "5%" in tl or "10%" in tl:
                pass
            elif "russian" in tl and "ashkenazi" in tl:
                return "Founder", "Founder_mixed", "Russian + Ashkenazi"
            else:
                return "Founder", "Founder_mixed", "Jewish + European"
        if has_eur and has_me:
            return "Admixed", "EUR+ME", "European + Middle Eastern + Jewish"

    # ── Mexican + Jewish ──
    if has_mex and has_jew:
        return "Admixed", "EUR+AMR", "Mexican Sephardic Jewish"

    # ── Admixed: EUR + non-EUR ──
    if has_eur and len(non_eur) > 0:
        if len(non_eur) >= 2 or has_oce:
            return "Admixed", "Multi-continental", f"EUR + {'+'.join(non_eur)}"
        if has_me: return "Admixed", "EUR+ME", "European + Middle Eastern"
        if has_eas: return "Admixed", "EUR+EAS", "European + East Asian"
        if has_afr: return "Admixed", "EUR+AFR", "European + African"
        if has_sas: return "Admixed", "Multi-continental", "European + South Asian"
        if has_amr: return "Admixed", "EUR+AMR", "European + Americas"

    # ── Pure EUR → sub-region ──
    if has_eur and len(non_eur) == 0:
        regions = []
        if has_nw: regions.append("NW")
        if has_s:  regions.append("S")
        if has_e:  regions.append("E")
        if has_c:  regions.append("C")

        if len(regions) >= 3:
            return "EUR", "EUR_pan", "3+ European sub-regions"
        if len(regions) == 1:
            nm = {"NW": "Northwestern", "S": "Southern",
                  "E": "Eastern", "C": "Central"}
            return "EUR", f"EUR_{regions[0]}", f"{nm[regions[0]]} European"
        if set(regions) == {"NW", "S"}:
            return "EUR", "EUR_pan", "North + South European"
        if set(regions) == {"NW", "C"}:
            n_components = tl.count(",") + tl.count("+") + tl.count("/")
            if n_components >= 2:
                return "EUR", "EUR_pan", "Multiple NW + Central countries"
            return "EUR", "EUR_C", "NW + Central (Central emphasized)"
        if set(regions) == {"NW", "E"}:
            return "EUR", "EUR_E", "NW + Eastern (Eastern emphasized)"
        if len(regions) == 2:
            return "EUR", "EUR_pan", "Two European sub-regions"
        if len(regions) == 0 and has_gen:
            return "EUR", "EUR_pan", "Generic European label"
        return "EUR", "EUR_pan", "European (could not determine sub-region)"

    return "Unknown", "Vague_mixed", "Could not classify"


TIER1_CORRECTIONS = [
    ("british + northern european + eastern eupropean",
     "EUR_E", "NW + Eastern European; Eastern component more genetically distinctive in IBS"),
    ("British + northern european + eastern eupropean",
     "EUR_E", "Case variant of above"),
    ("British isles + central european + northern european",
     "EUR_NW", "NW majority (2/3); Central is genetically close to NW on the NW-C axis"),
    ("British Isles + Central European + Northern European",
     "EUR_NW", "Case variant of above"),
    ("British Isles, Western European, and Central European",
     "EUR_NW", "NW dominates (British + Western); Central is genetically close"),
    ("British isles, western european, and central european",
     "EUR_NW", "Case variant of above"),
    ("British isles, western european, Scandinavian and central european",
     "EUR_NW", "NW dominates (British + Western + Scandinavian = 3 NW, 1 C)"),
    ("British isles, western european, scandinavian and central european",
     "EUR_NW", "Case variant of above"),
    ("British, German, Irish",
     "EUR_NW", "2 NW (British, Irish) + 1 C (German); NW majority"),
    ("Scottish, German, Swiss",
     "EUR_C", "1 NW (Scottish) + 2 C (German, Swiss); Central majority"),
    ("Scottish, german, swiss",
     "EUR_C", "Case variant of above"),
    ("northern and southern european",
     "EUR_pan", "North + South spans full European N-S genetic axis; neither dominates"),
    ("Northern and southern european",
     "EUR_pan", "Case variant of above"),
    ("East European+British+French",
     "EUR_pan", "Three distinct regions (E + NW + NW); spans two sub-regions"),
    ("Irish, english, slavic,",
     "EUR_pan", "NW (Irish + English) + E (Slavic); two sub-regions, roughly split"),
    ("Jewish ashkenaz + sephardic",
     "Sephardic", "When both present, Sephardic is the more specific genetic identity"),
]


def main():
    raw = pd.read_csv(RAW_ANCESTRY_CSV)
    unique_values = sorted(raw["value"].str.strip().unique(), key=str.lower)
    print(f"Unique raw ancestry values to classify: {len(unique_values)}")

    # ── Auto-classify ──
    results = []
    for val in unique_values:
        t0, t1, justification = classify(val)
        results.append({
            "raw_ancestry": val,
            "tier0": t0,
            "tier0_justification": justification,
            "tier1": t1,
            "tier1_justification": justification,
        })

    mapping = pd.DataFrame(results)
    print(f"Auto-classified {len(mapping)} unique values")

    # ── Apply manual corrections ──
    n_corrected = 0
    for raw_val, new_t1, new_just in TIER1_CORRECTIONS:
        mask = mapping["raw_ancestry"] == raw_val
        if mask.sum() == 0:
            print(f"  WARNING: correction target not found: \"{raw_val[:60]}\"")
            continue
        old_t1 = mapping.loc[mask, "tier1"].values[0]
        if old_t1 != new_t1:
            mapping.loc[mask, "tier1"] = new_t1
            mapping.loc[mask, "tier1_justification"] = new_just
            n_corrected += 1
            print(f"  {old_t1:>15} → {new_t1:<15}  \"{raw_val[:60]}\"")
        else:
            print(f"  (already correct)              \"{raw_val[:60]}\"")

    print(f"\nManual corrections applied: {n_corrected}")

    # ── Summary ──
    print("\n" + "=" * 60)
    print("MAPPING SUMMARY")
    print("=" * 60)

    print(f"\nTier 0:")
    print(mapping["tier0"].value_counts().to_string())

    print(f"\nTier 0 × Tier 1:")
    cross = (mapping.groupby(["tier0", "tier1"]).size()
             .reset_index(name="n")
             .sort_values(["tier0", "n"], ascending=[True, False]))
    print(cross.to_string(index=False))

    # ── Save ──
    mapping.to_csv(MAPPING_CSV, index=False)
    print(f"\nSaved: {MAPPING_CSV}")


if __name__ == "__main__":
    main()
