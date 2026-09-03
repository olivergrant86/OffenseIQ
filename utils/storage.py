"""
Simple file-based persistence for OffenseIQ.

Everything lives in /data as JSON (library + rules) and CSV (master play log).
This is intentionally simple (no database) so the app works the moment it's
deployed. NOTE: on most free hosting (e.g. Streamlit Community Cloud) this
folder can reset when the app goes to sleep for a long time or is redeployed.
If you want the learned formations/rules to survive that, the next step is
to move this same read/write interface onto a small Supabase table (same
approach already used in DefensiveIQ) -- the rest of the app doesn't need to
change, only these functions.
"""
import json
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

FORMATION_LIB_PATH = os.path.join(DATA_DIR, "formation_library.json")
RULES_PATH = os.path.join(DATA_DIR, "alignment_rules.json")
MASTER_PLAYS_PATH = os.path.join(DATA_DIR, "master_plays.csv")


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


# ---------- Formation library (the "how it's drawn" memory) ----------

def load_formation_library():
    """dict: { formation_name: {"points": [{"label","x","y"}, ...], "notes": str} }"""
    return _load_json(FORMATION_LIB_PATH, {})


def save_formation(formation_name, points, notes=""):
    lib = load_formation_library()
    lib[formation_name] = {"points": points, "notes": notes}
    _save_json(FORMATION_LIB_PATH, lib)


def delete_formation(formation_name):
    lib = load_formation_library()
    if formation_name in lib:
        del lib[formation_name]
        _save_json(FORMATION_LIB_PATH, lib)


# ---------- Alignment rules (defaults + per-formation overrides) ----------

def load_rules():
    """
    {
      "defaults": [ {"match": {field: value, ...}, "call": {"front":..,"technique":..,"coverage":..}}, ... ],
      "formation_overrides": { formation_name: {"front":..,"technique":..,"coverage":..} }
    }
    """
    return _load_json(RULES_PATH, {"defaults": [], "formation_overrides": {}})


def save_rules(rules):
    _save_json(RULES_PATH, rules)


def add_default_rule(match_dict, call_dict):
    rules = load_rules()
    match_dict = {k: v for k, v in match_dict.items() if v not in (None, "", "Any")}
    rules["defaults"].append({"match": match_dict, "call": call_dict})
    save_rules(rules)


def delete_default_rule(index):
    rules = load_rules()
    if 0 <= index < len(rules["defaults"]):
        rules["defaults"].pop(index)
        save_rules(rules)


def set_formation_override(formation_name, call_dict):
    rules = load_rules()
    rules["formation_overrides"][formation_name] = call_dict
    save_rules(rules)


def clear_formation_override(formation_name):
    rules = load_rules()
    if formation_name in rules.get("formation_overrides", {}):
        del rules["formation_overrides"][formation_name]
        save_rules(rules)


def resolve_call(formation_name, play_row, rules=None):
    """
    Returns (call_dict, source_string) for a given formation name + a
    representative play row (pandas Series or dict) with columns like
    'FORM FAMILY', 'OFF STR', 'FIELD/BOUNDARY', 'ST/ WK', 'BACKFIELD'.
    Priority: formation-specific override > most-specific matching default rule > None.
    """
    if rules is None:
        rules = load_rules()

    override = rules.get("formation_overrides", {}).get(formation_name)
    if override:
        return override, "Saved call for this formation"

    best_rule = None
    best_score = -1
    for rule in rules.get("defaults", []):
        match = rule.get("match", {})
        if not match:
            continue
        ok = True
        for field, value in match.items():
            row_value = play_row.get(field) if isinstance(play_row, dict) else play_row.get(field, None)
            if pd.isna(row_value) if not isinstance(row_value, str) else False:
                row_value = None
            if row_value != value:
                ok = False
                break
        if ok and len(match) > best_score:
            best_score = len(match)
            best_rule = rule

    if best_rule:
        return best_rule["call"], f"Default rule ({', '.join(f'{k}={v}' for k, v in best_rule['match'].items())})"

    return None, "No call set yet"


# ---------- Master play log (accumulates across every upload) ----------

def load_master_plays():
    if not os.path.exists(MASTER_PLAYS_PATH):
        return pd.DataFrame()
    return pd.read_csv(MASTER_PLAYS_PATH)


def append_plays(new_df, source_label):
    new_df = new_df.copy()
    new_df["__source_file"] = source_label
    existing = load_master_plays()
    if existing.empty:
        combined = new_df
    else:
        combined = pd.concat([existing, new_df], ignore_index=True)
    combined.to_csv(MASTER_PLAYS_PATH, index=False)
    return combined
