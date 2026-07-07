# USEDC Sales IQ — Ayan's Modules

Sales Coach, Team Trends, and Sales School for the USEDC Sales IQ platform,
plus lightweight versions of the shared utilities so these tabs run and
demo standalone today, and merge cleanly with Asa's modules later.

> **Status:** 🎯 Sales Coach is live. 📊 Team Trends and 🎓 Sales School are
> next — the shell already routes to them and shows a placeholder until the
> files land in `pages/`.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app seeds 90 days of realistic sample call data on first launch, so
every chart and coaching view works immediately.

## AI modes

- **Demo mode (default):** no API key needed — `utils/ai.py` returns
  realistic deterministic content so you can demo offline.
- **Live mode:** `export OPENAI_API_KEY=sk-...` and every lesson, quiz,
  coaching report, and roleplay is generated live. No code changes.

## My tabs

| Tab | File | Highlights |
|---|---|---|
| 🎯 Sales Coach | `pages/sales_coach.py` | Per-rep AI coaching report grounded in real call stats: score gauge, weekly score trend, strengths/weaknesses, missed opportunities, "said vs. try instead" rewrites, discovery questions, closing techniques, weekly goals, manager notes saved to DB |
| 📊 Team Trends | `pages/team_trends.py` *(next)* | Auto-computed headline findings ("Tuesday afternoons convert best"), day×hour conversion heatmap, product interest & objection trend lines, calls per rep, territory conversion, duration distribution, leaderboard |
| 🎓 Sales School | `pages/sales_school.py` *(next)* | Personalized 4-week curriculum, weekly lesson + daily tip, **interactive objection roleplay** (AI plays the advisor and coaches your responses), scored quizzes, best-practices playbook, TED-Talk summaries |

## Merging with Asa

- The `calls` table schema in `utils/database.py` is the shared contract —
  Asa's Call Analyzer writes rows, my tabs read them. Review it together.
  Rows carry a `source` column (`analyzed` vs `sample`) so demo data and
  real data never mix.
- `utils/ai.py` exposes `generate()` / `generate_json()` — Asa's tabs can
  use the same functions.
- `app.py` already routes to `render_call_analyzer()`,
  `render_knowledge_base()`, and `render_ai_insights()` — dropping those
  files into `pages/` activates them with no other changes.
- Sample data lives only in `utils/sample_data.py` (`seed_if_empty()`),
  so it never overwrites real analyzed calls.

## Structure

```
usedc-sales-iq/
  app.py                  # shell: branding, nav, routing only
  .streamlit/config.toml  # theme + disables auto page nav
  pages/
    sales_coach.py        # render_sales_coach()
    team_trends.py        # render_team_trends()   (next)
    sales_school.py       # render_sales_school()  (next)
  utils/
    ai.py                 # generate(), generate_json(), demo fallback
    database.py           # schema + query helpers (SQLite → Postgres-ready)
    sample_data.py        # deterministic 90-day demo dataset
    charts.py             # shared Plotly theme + chart builders
  data/                   # sales_iq.db lives here (gitignored)
  requirements.txt
```
