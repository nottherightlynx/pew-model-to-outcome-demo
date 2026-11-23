# Adaptive content optimization engine — accessible Streamlit upgrade

**This upgrade is a complete, independent candidate demo—not a Pew internal application.** It preserves the five-variable model (audience, organic co-occurrence, semantic/entity language, technical readiness, and platform format), with different settings per research portfolio. It does not promise specific algorithm rankings, traffic gains or AI citations.

## Install inside the existing `pew-model-to-outcome-demo`

1. Unzip the package into Downloads or directly inside your project. Keep the `pew_optimizer_upgrade` directory intact.
2. In Terminal, open your *existing* `pew-model-to-outcome-demo` directory and run:

```bash
python3 /path/to/pew_optimizer_upgrade/install_upgrade.py
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-upgrade.txt
python -m pytest -q tests
python -m streamlit run app_v2.py
```

If you unzip the file *inside* your project, use the literal install command:

```bash
python3 pew_optimizer_upgrade/install_upgrade.py
```

**No existing `app.py`, `scoring.py`, `rules.py`, data fixtures or YAML portfolios are overwritten.** Your original app still runs. The upgraded version has its own entry point: `app_v2.py`. Re-running the installer does not overwrite modified target files; it preserves a backup and refuses by default. See `docs/UPGRADE_STRATEGY_AND_SOURCES.md`.

## What's new

- **Accessibility and mobile:** one scroll; all selectors on the main page; native controls with labels; one-column reading order; clear text next to charts and equivalent accessible data. No custom CSS targeting Streamlit internals or untrusted HTML injection.
- **GEO / LLM search:** check visible factual text, titles/headings, data/visual alternatives, crawl/index eligibility and valid optional JSON-LD. No unsupported claims that schema, exact keyword repetition or unlinked mentions guarantee citations. Google and OpenAI documentation are linked in the method document.
- **Less exploitable:** local data only, bounded file sizes, blocked path traversal, safe YAML, strict finite numeric values, aggregate-only analytics, source labels, CSV formula-injection defense, and no autonomous publishing or web requests.
- **More scalable:** YAML-configured portfolio and platform selection; reusable pure scoring/audit functions; analytics source contracts; original five-factor formula preserved.
- **More relevant to documented Pew tools:** Pew's privacy policy discloses Google Analytics. Its job posting names Google Tag Manager and Facebook Insights skills, along with SQL, Python/R, dbt-compatible transformations and BI. The demo uses **synthetic** GA-like data; it does not assert access to or use of Pew accounts. Google Search Console is OPTIONAL, not confirmed as deployed.

## Which file does what?

| File | Purpose |
|---|---|
| `app_v2.py` | One-scroll responsive, two-audience UX; charts, actions, limitations, synthetic metrics |
| `validation_v2.py` | Safe YAML and local fixture validation; prevents NaN, traversal and excessive inputs |
| `model_v2.py` | Five-factor formula and explainable provenance; search noindex eligibility gate |
| `seo_audit_v2.py` | Documented, non-predictive HTML/GEO + WCAG checks and exact action proposals |
| `recommendations_v2.py` | Merges formula-driven priorities with evidence-backed audit recommendations |
| `analytics_contract_v2.py` | Aggregate-only, explicitly labeled synthetic GA / optional Search Console / role-mentioned Facebook metrics |
| `rule_review_v2.py` | Documentation proposals only; cannot change weights or publish edits |
| `tests/test_upgrade_v2.py` | Unit tests for model, inputs, safety and provenance |
| `docs/UPGRADE_STRATEGY_AND_SOURCES.md` | Rationale, official sources, role-stack evidence labels and limitations |

## Boundaries

The user-defined score is a prioritization heuristic, **not a tested probability or a Google/LinkedIn/YouTube ranking factor**. The co-occurrence fixture is synthetic; do not manufacture mentions or scrape restricted forums. The source audit flags issues for human review; it is not a substitute for manual accessibility audits, privacy review, Search Console, research-fidelity review, platform permission or genuine experiments.
