# Upgrade strategy, source discipline, and design controls

**Date: 23 November 2026. Candidate-owned, independent prototype.** The engine remains an **adaptive cross-platform content analysis and optimization system**. The five factors and their weighted diagnostic formula are intact. The change is to what the program treats as evidence, how it communicates gaps, and how it maintains usability and safety as portfolios are added.

## 1. Exactly which analytics tools are grounded in public Pew evidence?

| Tool | What we know publicly | What the code does |
|---|---|---|
| **Google Analytics** | Pew explicitly says its website uses Google Analytics in its privacy policy. Source: https://www.pew.org/en/about/privacy-policy | A synthetic **aggregate-only**, Google Analytics-like export demonstrates later performance evaluation. No Pew account or property is accessed. The privacy notice does not itself specify the GA version, implementation details or event taxonomy. |
| **Google Tag Manager** | The official Officer, Digital Analytics and Insights, Communications vacancy lists Google Tag Manager expertise. Source: https://pewtrusts.wd5.myworkdayjobs.com/TrustsExternal/job/Officer--Digital-Analytics-and-Insights--Communications_R003312 | The integration contract shows where approved tag/metric definitions would enter. **The posting is not proof that Pew currently deploys GTM.** |
| **Facebook Insights** | The same vacancy lists Facebook Insights proficiency. | The contract reserves named metrics and review requirements. Synthetic metrics can be supplied; no live Meta connection, tokens, or platform access is embedded. The posting is not proof of current account integration. |
| **SQL; Python/R; dbt or comparable data transformations; BI** | The vacancy explicitly requests technical expertise in these. | Python files are separable and tested, aggregate tables have a stable contract, and `sql/quality_checks.sql` illustrates SQL/dbt-compatible tests. This is a *candidate demonstration*, not Pew's architecture. |
| **Google Search Console** | Official Google documentation describes its Search Analytics API, but the public Pew job posting does **not establish** that Pew uses it. | Explicitly named `search_console_proposed`, entirely synthetic. A future verified, authorized integration could use the official API subject to quotas and access control. |
| **Cloud LLM / third-party search or listening vendor** | No particular such product is confirmed in the job evidence used here. | Not enabled. The prototype relies on local deterministic checks and synthetic observations; no uncontrolled model calls, prompt injection or vendor dependencies. |

**Important:** Distinguish "listed as an applicant skill" from "confirmed as deployed at Pew". The demo never claims actual Pew engagement, access credentials, operational architecture, internal attribution or partnership approval.

## 2. SEO / GEO: how the original model is upgraded without replacing it

**Your working formula:** `AVS(platform) = 100 × Σ(weight[i] × factor[i]) ÷ Σ(available weight[i])`, with five factors `audience`, `cooccurrence`, `semantic`, `technical`, `format`. The fixed, configured weights are hypotheses. They are not learned coefficients and the result is not actual AI-search appearance probability. Noindex is displayed as a distinct search-eligibility constraint. Co-occurrence is synthetic, and no app process creates or solicits inorganic mentions.

**A — Audience / platform.** Retain portfolio-specific fit assumptions and plain-language audience definitions. Compare these with *authorized* qualitative research and owned-channel engagement. No universal cross-platform dwell-time coefficient is assumed.

**C — Independent co-occurrence.** Show the topic’s conversation context without treating mention frequency as a hidden ranking rule. Google's November 2026 generative AI guidance cautions against seeking inauthentic mentions. The demo uses no unauthorized public-community scraping or outreach automation.

**S — Semantic and entity-first content.** Check the actual visible text for portfolio-defined questions and anchor terminology. Preserve correct sector vocabulary alongside plain-English descriptions. The current implementation is a **bounded lexical proxy**, not a vector embedding search or proof of relevance. Add editorial review rather than inventing semantic matches.

**T — Technical + multimodal availability.** Audit a source HTML fixture for an honest page title, heading structure, extractable main text, language, links, image alternatives, and malformed optional JSON-LD. For charts and maps, flag missing text context for human review; distinguish `alt=""` on genuinely decorative images from missing alt. A `noindex` directive is an eligibility flag. A missing canonical or JSON-LD block is **not a universal defect**. Google says existing SEO remains foundational for its AI experiences; there is no special schema.org markup required just to appear in AI Overviews/AI Mode. If using structured data, it should describe visible content faithfully, and eligibility for rich results is not guaranteed.

**P — Platform presentation.** Continue identifying different appropriate packaging by audience and channel. Current `desired_format` entries remain hypotheses and reviewable recommendations; never imply that a particular word count, outbound-link practice, carousel style or video hook guarantees reach. Google explicitly recommends usable image/video content and helpful non-commodity content rather than scaled search-manipulation.

**From diagnosis to recommendation:** show action, reason, supporting page evidence, original platform factor, and who reviews it. The fixed scoring formula can increase after a hypothetical change without any real increase in observed traffic or AI citations. A meaningful implementation study would compare *approved*, baseline-normalized outcome metrics after changes to equivalent content.

**RSS / updates:** official documentation entries produce review proposals only; rule changes require a human approver, version, source diff and regression tests. The interface's example queue is static and clearly labeled; there is no live RSS polling in the candidate demo.

## 3. Mobile, accessibility and readability

- **One scroll:** the research portfolio, platform and explanation switch appear at the top of the main page, not inside a collapsed sidebar. The remaining sections flow vertically. Avoid wide factor heatmaps or multi-column layouts that become unreadable on phones.
- **Plain language in both modes:** Non-technical explains the question, the gap and the recommended change. Technical adds the actual calculation, weights, data provenance, uncertainty, official references and data quality. Neither claims the score is an algorithm's private ranking.
- **Built-in accessibility primitives:** use native `st.selectbox`, `st.radio`/`st.segmented_control`, headings, `st.metric`, `st.bar_chart`, `st.dataframe`, readable text alternatives, and keyboard-usable link elements. No injected JS and no HTML cards with unverified contrast or invisible focus styles.
- **Native theming:** `.streamlit/config.toml` sets legible contrast and a neutral palette without brittle targeting of Streamlit's internal DOM. Actual device, screen-reader, zoom and WCAG 2.2 audits remain necessary. The code is not an accessibility certification.
- **Charts always have textual equivalents:** a chart can be insufficient by itself to communicate a result. The platform scores are repeated in text, technical tables preserve factor values, and charts carry an alt parameter in Streamlit versions that support it.

Primary documentation: https://docs.streamlit.io/develop/concepts/design/best-practices ; https://docs.streamlit.io/develop/concepts/design/charts ; https://www.w3.org/TR/WCAG22/ (esp. 1.4.10 Reflow, 1.4.3 Contrast, 2.1 keyboard, headings and image alternatives).

## 4. Security and minimal exploitability

- **Bounded input:** `validation_v2.py` enforces 80 KB YAML configuration, 1 MB local HTML fixture / observation CSV, at most 24 portfolio configs, 20 platforms/portfolio, 40 topic terms, known factor keys and `math.isfinite` weights. It rejects absolute/traversal/symlink escapes outside the correct local folder.
- **Trusted parsing:** YAML is loaded with `yaml.safe_load`; HTML is treated as data and never executed; JSON-LD is parsed with `json.loads`, not evaluated. No arbitrary URL ingestion or network requests, avoiding unauthorized crawling and common server-side request-forgery pitfalls.
- **No injected HTML/CSS/JS:** contrast and layout use Streamlit's theme, not `unsafe_allow_html=True`. This avoids dependence on unstable internal CSS selectors and minimizes script insertion surfaces. Rich text from fixtures is not rendered as raw HTML.
- **Data minimization:** synthetic metrics are aggregate counts with approved source/metric identifiers and date windows. No contact IDs, email addresses, cookies, profiles, tokens, or surveillance of particular users. No analytics keys are stored in the repository.
- **Output hygiene:** the CSV review queue escapes leading formula characters that may be executed when opened in spreadsheet software.
- **Restricted change workflow:** recommendation drafts require editorial approval; documentation notices do not rewrite weights or publish assets. A production, remotely hosted system requires authentication, RBAC, encrypted credentials, logging, and a thorough security assessment beyond this candidate demo.

Primary documentation: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html ; https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html ; https://docs.streamlit.io/develop/concepts/design/best-practices ; https://docs.streamlit.io/develop/concepts/connections/security-reminders.

## 5. Scalable analytics engineering rather than one-off dashboards

- A portfolio is **configuration**: an audience, terms, platforms and weighted hypotheses, not a new codebase.
- Processing is **modular**: `validation_v2` → `seo_audit_v2` / `model_v2` → `recommendations_v2` → Streamlit explanation. Pure functions can later be called by scheduled batch processing, a warehouse transformation or a documented API; the app does not hard-code platform names.
- The downstream metrics are **properly modeled**: `portfolio_id + platform + source + metric + date window` are the basic join keys. Keep Google Analytics sessions, Search Console impressions and Facebook post engagements in separate units. `sql/quality_checks.sql` shows relational uniqueness and provenance controls.
- Connection to an authorized Google Analytics source should use the *documented* Data API and its quotas, not screen-scraping or a shared personal access token. Any Search Console integration would similarly require site permission and API quota handling. Platform APIs are not a substitute for user access approval.
- Production load would need deduplicated asset IDs, a governed catalog, scheduled transforms, role-level permissions, monitoring, change approvals, and experiment data quality controls. Those are future requirements, **not capabilities of this local demo**.

Primary documentation: https://developers.google.com/analytics/devguides/reporting/data/v1/quotas ; https://developers.google.com/webmaster-tools/v1/how-tos/search_analytics ; https://developers.google.com/webmaster-tools/limits ; https://docs.streamlit.io/develop/concepts/design/performance.

## 6. Verified official source links (retrieved 23 November 2026)

1. The Pew Charitable Trusts — Officer, Digital Analytics and Insights, Communications, official Workday listing: https://pewtrusts.wd5.myworkdayjobs.com/TrustsExternal/job/Officer--Digital-Analytics-and-Insights--Communications_R003312
2. The Pew Charitable Trusts — Privacy policy, Google Analytics use and personal data: https://www.pew.org/en/about/privacy-policy
3. Google Search Central — Generative AI search guidance: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
4. Google Search Central — Helpful, reliable, people-first content: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
5. Google Search Central — Structured-data policies (no guaranteed appearance): https://developers.google.com/search/docs/appearance/structured-data/sd-policies
6. Google Search Central — Image SEO, alt text and nearby context: https://developers.google.com/search/docs/appearance/google-images
7. Google Search Central — JavaScript SEO; Googlebot can render JS with limits: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
8. OpenAI developer docs — Distinct search/training/user agents and webmaster controls: https://developers.openai.com/api/docs/bots
9. W3C — WCAG 2.2: https://www.w3.org/TR/WCAG22/
10. Streamlit — Design best practices: https://docs.streamlit.io/develop/concepts/design/best-practices
11. Streamlit — Chart design and accessible naming: https://docs.streamlit.io/develop/concepts/design/charts
12. OWASP — SSRF prevention: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
13. OWASP — Prompt injection prevention: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
14. Google — Analytics Data API quotas: https://developers.google.com/analytics/devguides/reporting/data/v1/quotas
15. Google — Search Console API analytics and limits: https://developers.google.com/webmaster-tools/v1/how-tos/search_analytics ; https://developers.google.com/webmaster-tools/limits

## 7. Acceptance and honest limits

**Pass:** original five-factor model is preserved; original `app.py` untouched; all code compiles; old and new tests pass on sample fixtures; portfolio switch changes results and actions; no `unsafe_allow_html=True`, dynamic remote fetches or stored secrets; color is not the only way to read a score; audit details have reasons and evidence links; CSV does not turn formulas into spreadsheet commands; mobile layout uses one column.

**Not yet proven:** accessibility conformance on an actual screen reader, real platform algorithm effects, ranking/citation lift, actual Pew technology deployment beyond public evidence, API integrations, accurate off-site organic mention coverage, authorization to run analytics inside Pew, production multi-tenancy, or suitability of the chosen demo weights.
