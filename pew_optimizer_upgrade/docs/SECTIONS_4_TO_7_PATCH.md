# Sections 4–7: platform-specific communication and technical insight upgrade

This is a **targeted presentation and decision-support patch**. It retains the five-factor formula, scoring weights, synthetic observations, portfolio YAML, technical audits, prioritization rules, and previous screens 1–3. The only edited original application files are `app_v2.py` and the installer's `FILES` manifest. Other original files are unchanged byte-for-byte. New files are `platform_insights_v2.py`, this change note and regression tests.

## What was fixed

Previously, the app changed the selected platform's score but repeated nearly the same narrative about recommendations, scenario testing, measurement and documentation. The fixed sections are generated from a **reviewable platform strategy**, selected portfolio and actual computed factor gaps. They intentionally produce distinct messages for both stakeholder groups.

| Section | Non-technical (Communications) | Technical (Data/IT/engineering + research/portfolio when relevant) |
|---|---|---|
| 4. What needs to change | Platform-specific content package, audience relevance, gap to fix, who approves | Concrete technical handoff, factors/evidence/priority, data provenance, research-fidelity and portfolio reviews |
| 5. What if we fix one gap? | A tangible change in format, heading, visual, transcript or framing for the selected platform | Which input is adjusted, configured weight, implementation checks, experiment limitations |
| 6. How we know | Which outcome matters for the selected platform and a Communications-friendly experiment | Named authorized metrics, source/denominator boundaries, join keys, QA, research approval, measurement limitations |
| 7. Strategy update | The specific content guidance a team should revisit when official guidance changes | Source-version/review/test/approval checklist and official documentation specific to the selected platform |

### Platform distinction

- **Search:** index eligibility, useful answer text, extractable tables and source links; Search Console is only a **proposed** source, while GA metrics are separate first-party metrics.
- **LinkedIn:** professional relevance, useful/native visual packaging, contextual caveats; LinkedIn-owned metrics are **not** in the offline fixture, GA referral counts are not substituted for native impressions.
- **YouTube:** opening/thumbnail appeal, accurate captions, source-linked description and retention validation; YouTube Studio data is **not** connected, and GA referrals do not measure retention.

The app uses native, labeled Streamlit controls and a single vertical flow. No raw HTML or new network calls are added. All external links are explicitly curated official reference pages. Documentation references are **static**, not live alerts, and **do not** change scoring weights.

## Install into an existing `pew-model-to-outcome-demo`

From the project root, after copying the ZIP to `~/Downloads`:

```bash
unzip -o ~/Downloads/Pew_Accessible_GEO_Optimizer_Platform_Insights_Fixed.zip -d .
python3 pew_optimizer_upgrade/install_upgrade.py --dry-run --force
python3 pew_optimizer_upgrade/install_upgrade.py --force
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-upgrade.txt
python -m pytest -q tests
python -m streamlit run app_v2.py
```

`--force` is needed if the earlier `app_v2.py` is installed. The installer stores a timestamped backup of changed upgrade files under `.pew-upgrade-backups/` and does **not** touch the original `app.py`, `scoring.py`, `rules.py`, YAML, or fixtures. The new regression tests check all three platforms, both audiences, source-safe metric rates and unchanged score arithmetic.

## Evidence and boundaries

- [Google Search Central: optimizing for AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [LinkedIn Help: how its Feed ranks content](https://www.linkedin.com/help/linkedin/answer/a9554004)
- [YouTube Help: content performance and recommendations](https://support.google.com/youtube/answer/16559650?hl=en)

Official platform documentation describes broad relevant practices and performance indicators; it **does not** reveal full proprietary ranking formulas. The engine's model scores are not predictions of reach, traffic, retention or citation probability. No real Pew data is accessed.
