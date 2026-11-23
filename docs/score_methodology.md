# Score methodology — model-to-outcome candidate demo

## Purpose
The core invention proposed here is a **prescriptive, adaptive cross-platform content optimizer**, not a conventional dashboard. It analyzes the conditions under which a particular audience may discover and engage with a piece of content, surfaces gaps, recommends specific changes, and supports subsequent tests. The score is a routing aid for decisions, **not** a published algorithm score or prediction of traffic, ranking, citations, or impact.

## Five modeled dimensions

1. **Audience/platform fit (A):** the portfolio's assumed relative audience presence and information needs on each platform. Configured in YAML; must eventually be validated with audience research and permitted channel analytics.
2. **Organic third-party co-occurrence (C):** a *synthetic observation proxy* of independently originated conversation mentioning the relevant subject in credible contexts. Demo formula: `min(mentions / 20, 1) × (qualified_mentions / mentions)`, with zero when there are no mentions. The threshold of 20 is **arbitrary for demonstration**, not a ranking factor. Never manufacture conversation or scrape without authorization.
3. **Semantic/entity fit (S):** share of configured priority multiword terms present in visible page text. This is an intentionally simple recall proxy, not a semantic embedding or evidence of meaning/satisfaction. Future research should test phrase variants, embeddings and factual quality with human judgments.
4. **Technical readiness (T):** fraction of six deterministic checks passed (one H1, subheadings, a meta description, canonical URL, image alternatives, sufficient extractable HTML). Absence of any single check does not imply a search penalty. Structured data is inspected but not universally scored as a ranking factor.
5. **Platform-format fit (P):** an illustrative assumption about how well current packaging serves a platform and audience. For production, operationalize with controlled tests and platform-authorized analytics.

## Formula
For configured nonnegative weights `w_i` summing to one and normalized component values `x_i ∈ [0,1]`:

`DemoDiagnosticScore = 100 × Σ(w_i × x_i)`, only across observed dimensions; if a component is missing, the score renormalizes over available weights and separately publishes `coverage = Σ(available weights)`. **Missing is never silently zero.** No universal factor weights are asserted.

The original conversation's freshness multiplier was supplied by an earlier assistant and is not treated as an empirically validated determinant. Official RSS/documentation updates should instead trigger human-reviewed, versioned rule proposals and regression tests.

## Recommendation priority
`ScenarioPriority = 100 × gap × configured_weight × mission_value / assumed_effort_hours`.

This is an **illustrative gap-to-effort ordering**, not expected visibility lift. A production decision rule should separately estimate effect sizes and uncertainty, editorial/research risk, accessibility impact, and implementation effort from experimental evidence.

## Data provenance
The two HTML source fixtures and all channel observations are fabricated for testing. They are not copied from Pew and are not statements of Pew's actual digital performance. Public institutional/standard links in `source_register.csv` are context only. The app uses no live crawling, social media API, analytics account, or AI engine calls.

## Appropriate evaluation
Pre-register a portfolio-specific channel outcome (qualified search traffic, content engagement, video completion, audience-relevant citations when available), plus accuracy/accessibility guardrails. Test one intervention at a time where feasible; distinguish randomized experimental comparisons from observational before/after changes. Avoid causal claims where suitable controls are absent. Examine whether the combined model generates higher-value suggestions than independent technical/semantic/platform audits.

## Governance
All public-facing edits and rule updates require human approval. Only authorized APIs or licensed datasets should ever be ingested. Honor privacy, copyright, platform terms and nonpartisanship requirements; follow W3C WCAG 2.2 for accessibility review. Do not turn organic co-occurrence analysis into stealth promotion.
