# USEDC Sales IQ — Ayan's Modules

Sales Coach, Team Trends, and Sales School for the USEDC Sales IQ platform,
plus lightweight versions of the shared utilities so these tabs run and
demo standalone today, and merge cleanly with Asa's modules later.

> **Status:** All three tabs are live — 🎯 Sales Coach, 📊 Team Trends
> (individual-first with a whole-team view), and 🎓 Sales School.

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
| 🎯 Sales Coach | `pages/sales_coach.py` | Per-rep AI coaching report grounded in real call stats: score gauge, weekly score trend, **delivery signals** ("You interrupted investors 6 times this week", pace vs recommended, explanation length vs top performers, talk ratio, open-ended questions), skill-area profile, strengths/weaknesses, missed opportunities, "said vs. try instead" rewrites, discovery questions, closing techniques, weekly goals, manager notes saved to DB |
| 📊 Team Trends | `pages/team_trends.py` | Auto-computed headline findings ("Tuesday afternoons convert best"), day×hour conversion heatmap, product interest & objection trend lines, calls per rep, territory conversion, duration distribution, leaderboard |
| 🎓 Sales School | `pages/sales_school.py` | Personalized 4-week curriculum (week 1 targets the rep's biggest data-flagged gap), weekly lesson + daily tip, **interactive objection roleplay** (AI plays a skeptical investor and coaches every response with a 0–100 score), scored quizzes weighted to weak areas, best-practices playbook, TED-Talk summaries |

## Merging with Asa

- The `calls` table schema in `utils/database.py` is the shared contract —
  Asa's Call Analyzer writes rows, my tabs read them. Review it together.
  Rows carry a `source` column (`analyzed` vs `sample`) so demo data and
  real data never mix. Delivery metrics (`interruptions`, `talk_ratio`,
  `words_per_minute`, `open_questions`, `avg_monologue_sec`, `skills`)
  are nullable — the Call Analyzer fills what it can and Sales Coach
  degrades gracefully when they're missing.
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
    team_trends.py        # render_team_trends()
    sales_school.py       # render_sales_school()
  utils/
    ai.py                 # generate(), generate_json(), demo fallback
    database.py           # schema + query helpers (SQLite → Postgres-ready)
    sample_data.py        # deterministic 90-day demo dataset
    charts.py             # shared Plotly theme + chart builders
  data/                   # sales_iq.db lives here (gitignored)
  requirements.txt
```
