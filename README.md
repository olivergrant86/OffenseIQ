# OffenseIQ — Offensive Scout Cards

Turns Hudl offensive playlist exports into scout cards: run/pass and personnel
tendencies per formation, a diagram of how each formation lines up (that you
teach it once and it remembers), and your defensive call for that look.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (same flow as DefensiveIQ)
1. Push this folder to a new GitHub repo.
2. Streamlit Community Cloud → New app → point at the repo, main branch, `app.py`.
3. Every push to main auto-redeploys.

## How it works
- **Upload Playlists**: drop in one or more Hudl playlist `.xlsx` files. Plays
  accumulate in `data/master_plays.csv` across every upload — nothing is lost
  between sessions.
- **Formation Library**: the first time a formation shows up, draw it once
  (drag the sliders to place X/Z/Y/H/F/etc., or copy a close formation and
  tweak it). Saved to `data/formation_library.json` and reused automatically
  on every future card with that same formation name.
- **Alignment Rules**: set default calls that apply automatically by formation
  family / strength / hash / etc. (most specific match wins), and/or lock in
  an exact call for one specific formation name as an override.
- **Scout Cards**: one card per formation — diagram + tendencies + your
  resolved call, with a quick per-card override box (optionally "save as
  default" right from the card). Export the whole set to PowerPoint.

## ⚠️ One thing to know about persistence
Formation drawings, rules, and the play database are stored as plain files in
`/data`. That's simple and works immediately, but on some free hosts (e.g.
Streamlit Community Cloud) that folder can reset if the app sleeps for a long
time or gets redeployed. If that ever bites you, the fix is dropping the same
read/write calls in `utils/storage.py` onto a Supabase table — same one
DefensiveIQ already uses — without touching the rest of the app.
