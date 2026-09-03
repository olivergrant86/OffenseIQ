"""
Parses Hudl-style playlist exports (the same column layout DefensiveIQ uses)
and computes per-formation tendencies for scout cards.
"""
import pandas as pd

EXPECTED_COLUMNS = [
    "PLAY #", "ODK", "OPP TEAM", "SERIES", "QTR", "SCORE", "DN", "DIST",
    "HASH", "YARD LN", "FORM FAMILY", "OFF FORM", "BACKFIELD", "OFF PLAY",
    "ST/ WK", "FIELD/BOUNDARY", "MOTION", "MOTION TO/ AWAY", "MOTION DIR",
    "PLAY TYPE", "FIB", "GN/LS", "RESULT", "PENALTY", "PLAY DIR",
    "RECEIVER_Jersey", "RECEIVER_Name", "PASSER_Jersey", "PASSER_Name",
    "RUSHER_Jersey", "RUSHER_Name", "OFF STR", "BENCH", "EFF",
]


def read_playlist(file) -> pd.DataFrame:
    """Reads an uploaded Hudl playlist .xlsx into a DataFrame, keeping only
    offensive snaps (ODK == 'O') since these are offensive scout cards."""
    df = pd.read_excel(file, sheet_name=0)
    df.columns = [str(c).strip() for c in df.columns]
    if "ODK" in df.columns:
        df = df[df["ODK"].astype(str).str.upper().str.startswith("O")]
    # normalize formation name so trivial casing/whitespace differences
    # don't create duplicate "unlearned" formations
    if "OFF FORM" in df.columns:
        df["OFF FORM"] = df["OFF FORM"].astype(str).str.strip()
    return df.reset_index(drop=True)


def formation_summary(master_df: pd.DataFrame) -> pd.DataFrame:
    """One row per unique OFF FORM with play count + last-seen opponent, used
    to show which formations are already in the library vs. need drawing."""
    if master_df.empty:
        return pd.DataFrame(columns=["OFF FORM", "FORM FAMILY", "plays"])
    g = (
        master_df.groupby("OFF FORM")
        .agg(
            plays=("OFF FORM", "count"),
            FORM_FAMILY=("FORM FAMILY", lambda s: s.mode().iat[0] if not s.mode().empty else ""),
        )
        .reset_index()
        .rename(columns={"FORM_FAMILY": "FORM FAMILY"})
        .sort_values("plays", ascending=False)
    )
    return g


def _pct(series, value_check):
    if len(series) == 0:
        return 0.0
    return round(100 * value_check(series).sum() / len(series), 1)


def formation_tendencies(master_df: pd.DataFrame, formation_name: str) -> dict:
    """Aggregated tendency stats for one formation, across every game uploaded so far."""
    rows = master_df[master_df["OFF FORM"] == formation_name]
    if rows.empty:
        return {}

    play_type = rows["PLAY TYPE"].fillna("Unknown")
    run_pct = _pct(play_type, lambda s: s.str.upper().eq("RUN"))
    pass_pct = _pct(play_type, lambda s: s.str.upper().eq("PASS"))

    top_plays = (
        rows["OFF PLAY"].fillna("Unknown").value_counts().head(5)
    )
    top_backfields = (
        rows["BACKFIELD"].fillna("Unknown").value_counts().head(3)
    )
    strength = rows["OFF STR"].fillna("Unknown").value_counts()
    strength_pct = {k: round(100 * v / strength.sum(), 1) for k, v in strength.items()} if strength.sum() else {}

    field_bound = rows["FIELD/BOUNDARY"].fillna("Unknown").value_counts()
    fb_pct = {k: round(100 * v / field_bound.sum(), 1) for k, v in field_bound.items()} if field_bound.sum() else {}

    avg_dist = rows["DIST"].dropna().mean() if "DIST" in rows.columns else None
    down_counts = rows["DN"].dropna().astype("Int64").value_counts().sort_index() if "DN" in rows.columns else pd.Series(dtype=int)

    motion_rate = _pct(rows["MOTION"].fillna(""), lambda s: s.str.strip().ne(""))

    return {
        "total_plays": len(rows),
        "run_pct": run_pct,
        "pass_pct": pass_pct,
        "top_plays": top_plays,
        "top_backfields": top_backfields,
        "strength_pct": strength_pct,
        "field_boundary_pct": fb_pct,
        "avg_distance": round(avg_dist, 1) if avg_dist is not None and pd.notna(avg_dist) else None,
        "down_counts": down_counts,
        "motion_rate": motion_rate,
        "representative_row": rows.iloc[0].to_dict(),
        "form_family": rows["FORM FAMILY"].mode().iat[0] if not rows["FORM FAMILY"].mode().empty else "",
    }
