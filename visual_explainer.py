"""One-scroll, responsive model-to-outcome explainer for the existing Streamlit app.

Reads the EXISTING scoring.py and rules.py. Uses illustrative portfolio fixtures.
This does not measure or promise real-world visibility or proprietary rankings.
"""
from __future__ import annotations

from html import escape
from typing import Any, Callable

import plotly.graph_objects as go
import streamlit as st

from rules import generate_recommendations
from scoring import COMPONENTS, calculate_score, normalize_weights, score_asset

DISPLAY = {
    "audience": ("Audience-platform match", "Who is likely to need this information here?", "Configured prior on qualified audience concentration; not measured reach."),
    "cooccurrence": ("Organic topic mentions", "Is this topic appearing in relevant independent conversations?", "Synthetic qualified-mention coverage × relevance proxy; data rights and sampling may constrain real use."),
    "semantic": ("Meaning and entity alignment", "Can readers and search systems understand the important concepts?", "Literal term coverage against a portfolio vocabulary; not semantic retrieval or embedding similarity."),
    "technical": ("Technical discoverability", "Can pages and visuals be understood and accessed reliably?", "Deterministic HTML checks: headings, meta description, canonical, image alternatives, and visible text."),
    "format": ("Platform-content fit", "Is this content packaged appropriately for this audience and channel?", "Configured or synthetic format-fit estimate, not a platform ranking signal."),
}

COLORS = {
    "audience": "#3C6E91",
    "cooccurrence": "#9563A6",
    "semantic": "#2D8F85",
    "technical": "#C1873A",
    "format": "#6674B8",
}

STYLE = """
<style>
.pew-flow {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.7rem;margin:.8rem 0 1.5rem;}
.pew-step {padding:1rem;border:1px solid rgba(125,125,125,.26);border-radius:.8rem;background:var(--secondary-background-color,#f3f5f8);min-width:0;}
.pew-step small {display:block;opacity:.78;line-height:1.45;margin-top:.45rem;}
.pew-step .num {font-size:.76rem;font-weight:700;opacity:.72;margin-bottom:.3rem;}
.pew-step strong {font-size:.96rem;line-height:1.3;display:block;overflow-wrap:anywhere;}
.pew-channel-card {padding:1rem 1.1rem;border:1px solid rgba(125,125,125,.26);border-radius:.8rem;margin-bottom:.75rem;background:var(--secondary-background-color,#f3f5f8);}
.pew-channel-card strong {font-size:1.06rem;}
.pew-channel-card p {margin:.4rem 0 0;line-height:1.5;overflow-wrap:anywhere;}
.pew-channel-card .subline {opacity:.75;font-size:.85rem;}
.pew-score-number {font-weight:750;font-variant-numeric:tabular-nums;}
@media(max-width:960px){.pew-flow{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media(max-width:600px){.pew-flow{grid-template-columns:minmax(0,1fr);}.pew-channel-card{padding:.8rem;}}
</style>
"""


def _contributions(result: dict[str, Any], weights: dict[str, float]) -> dict[str, float]:
    """Return weighted percentage-points actually used in score_asset's score."""
    normalized = normalize_weights(weights)
    values = result["components"]
    denominator = sum(normalized[k] for k in values)
    if denominator <= 0:
        return {k: 0.0 for k in COMPONENTS}
    return {k: 100 * normalized[k] * float(values.get(k, 0)) / denominator for k in COMPONENTS}


def _chart_contributions(results: dict[str, dict[str, Any]], weights: dict[str, float], focus: str) -> go.Figure:
    names = list(results)
    axis_labels = [("● " if p == focus else "") + p for p in names]
    fig = go.Figure()
    for key in COMPONENTS:
        contrib = [_contributions(results[p], weights)[key] for p in names]
        raw = [results[p]["components"].get(key) for p in names]
        fig.add_trace(go.Bar(
            name=DISPLAY[key][0], y=axis_labels, x=contrib, orientation="h",
            marker_color=COLORS[key],
            customdata=[[r if r is not None else -1, normalize_weights(weights)[key]] for r in raw],
            hovertemplate=(f"<b>{DISPLAY[key][0]}</b><br>Contribution: %{{x:.1f}} points"
                           "<br>Factor level: %{customdata[0]:.0%}"
                           "<br>Configured weight: %{customdata[1]:.0%}<extra></extra>"),
        ))
    fig.update_layout(
        barmode="stack", height=max(275, len(names) * 66 + 100),
        margin=dict(l=8, r=12, t=18, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 100], title="Illustrative diagnostic score (0–100)",
                   ticksuffix="", gridcolor="rgba(120,120,120,.13)"),
        yaxis=dict(autorange="reversed", title=None),
        legend=dict(orientation="h", y=-0.48, x=0, font=dict(size=10)),
    )
    return fig


def _chart_matrix(results: dict[str, dict[str, Any]]) -> go.Figure:
    names = list(results)
    labels = ["Audience", "Organic", "Semantic", "Technical", "Format"]
    matrix = [[results[p]["components"].get(k) for k in COMPONENTS] for p in names]
    txt = [["—" if value is None else f"{value:.0%}" for value in row] for row in matrix]
    fig = go.Figure(go.Heatmap(
        z=matrix, x=labels, y=names, zmin=0, zmax=1,
        colorscale=[[0.0, "#e8edf4"], [0.5, "#8dbbc8"], [1.0, "#2c657f"]],
        text=txt, texttemplate="%{text}", textfont=dict(size=12),
        colorbar=dict(title="Factor", tickformat=".0%", thickness=11),
        hovertemplate="%{y}<br>%{x}<br>Configured / observed proxy: %{z:.0%}<extra></extra>",
        hoverongaps=False,
    ))
    fig.update_layout(
        height=max(245, len(names) * 58 + 100),
        margin=dict(l=6, r=8, t=24, b=32),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed", title=None),
        xaxis=dict(side="top", tickangle=-22, automargin=True),
    )
    return fig


def _stage_cards(technical: bool) -> str:
    steps = (
        [
            ("Choose the audience", "Select a portfolio and compare the channels relevant to its audience."),
            ("Analyze five conditions", "Check audience fit, independent conversations, clarity, technical readiness and format."),
            ("Calculate the gaps", "Apply the portfolio's weights to expose weaknesses on each platform."),
            ("Recommend specific edits", "Rank editorial, format, metadata and distribution changes by scenario priority."),
            ("Test and revise", "Measure real outcomes later; review official documentation before changing scoring rules."),
        ] if not technical else [
            ("Load config + fixture", "YAML audience/channel priors and weights, HTML structural analysis, synthetic CSV proxies."),
            ("Compute x₁ … x₅", "score_asset() builds five normalized factors and records missing dimensions."),
            ("Normalize + aggregate", "100 × Σ(wᵢxᵢ)/Σ(wᵢ available); missing factors are excluded with coverage disclosed."),
            ("Prioritize changes", "rules.py ranks triggered interventions using gap × weight × mission value / effort."),
            ("Evaluate + govern", "Scenario scores are not experimental lift; source changes need review and regression tests."),
        ]
    )
    return '<div class="pew-flow">' + "".join(
        f'<div class="pew-step"><div class="num">STEP {i}</div><strong>{escape(title)}</strong>'
        f'<small>{escape(detail)}</small></div>'
        for i, (title, detail) in enumerate(steps, 1)
    ) + "</div>"


def render_visual_explainer(
    config: dict[str, Any],
    html: str,
    observation_loader: Callable[[str, str], dict[str, Any]],
    selected_platform: str | None = None,
) -> None:
    """Render a vertical, responsive explanation with all configured platforms.

    The existing sidebar can supply selected_platform; no extra platform selector.
    """
    st.markdown(STYLE, unsafe_allow_html=True)
    portfolio = config["portfolio_id"]
    platforms = list(config["platforms"])
    focus = selected_platform if selected_platform in platforms else platforms[0]
    results: dict[str, dict[str, Any]] = {}
    for platform in platforms:
        observation = observation_loader(portfolio, platform)
        results[platform] = score_asset(html, config, platform, observation)

    st.subheader(f"{config['portfolio_label']} — formula and platform logic")
    st.caption(f"Audience: {config['audience']}  |  Objective: {config['objective']}")
    technical = st.radio(
        "Explanation level", ["Non-technical", "Technical"], horizontal=True,
        key=f"pew_mode_{portfolio}",
    ) == "Technical"
    st.info("Illustrative prototype using synthetic platform observations, configured assumptions and local HTML fixtures. No real Pew engagement, proprietary ranking factor, or measured traffic lift is shown.")

    st.markdown("#### How the engine works")
    st.markdown(_stage_cards(technical), unsafe_allow_html=True)
    if technical:
        st.latex(r"S_{p}=100\,\frac{\sum_{i\in A_p} w_i x_{i,p}}{\sum_{i\in A_p} w_i}")
        st.caption("For platform p, Aₚ is the set of available dimensions. Values x are 0–1; configured weights w are normalized and not empirically estimated. Coverage = Σ available weights. This diagnostic is not actual probability of exposure or a proprietary platform score.")
    else:
        st.write("**How to read the score:** Each platform receives five checks. The portfolio gives some checks more importance than others. Their combined result helps prioritize edits—not predict how many people will see the content.")

    st.markdown("#### Compare all configured platforms")
    st.caption("Each colored segment contributes percentage points to that platform's illustrative total. The ● marks the channel chosen in the existing sidebar.")
    st.plotly_chart(_chart_contributions(results, config["weights"], focus), use_container_width=True, theme="streamlit")
    st.caption("The chart shows the five inputs behind the score; it does not imply a causal platform ranking formula.")

    st.markdown("#### Why platform scores differ")
    st.plotly_chart(_chart_matrix(results), use_container_width=True, theme="streamlit")
    st.caption("A percentage in a cell is a component value, not observed platform visibility. Empty/missing dimensions are not assumed to be zero.")

    if technical:
        st.markdown("#### Component definitions and provenance")
        weights = normalize_weights(config["weights"])
        for key in COMPONENTS:
            st.markdown(f"**{DISPLAY[key][0]} — weight {weights[key]:.0%}**: {DISPLAY[key][2]}")
    else:
        st.markdown("#### What the five factors mean")
        for key in COMPONENTS:
            st.markdown(f"**{DISPLAY[key][0]}:** {DISPLAY[key][1]}")

    st.markdown("#### Platform-by-platform implications")
    for platform, result in results.items():
        ranked = generate_recommendations(config, result)
        priority = ranked[0]["action"] if ranked else "No rule threshold triggered; review content quality and experiment design."
        missing = [DISPLAY[k][0] for k in COMPONENTS if k not in result["components"]]
        format_spec = config["platforms"][platform]["desired_format"]
        parts = (
            f'<div class="pew-channel-card"><strong>{escape(platform)}'
            f' <span class="pew-score-number">· {result["score"]:.1f}/100</span></strong>'
            f'<div class="subline">Data coverage {result["coverage"]:.0%} · '
            f'{"Current focus" if platform == focus else "Platform comparison"}</div>'
            f'<p><b>Best next action:</b> {escape(priority)}</p>'
            f'<p><b>Suggested asset:</b> {escape(format_spec)}</p>'
        )
        if technical:
            terms = [f'{normalize_weights(config["weights"])[k]:.2f}×{result["components"][k]:.2f}' for k in COMPONENTS if k in result["components"]]
            parts += f'<p class="subline">Calculation: 100 × ({escape(" + ".join(terms))}) / {result["coverage"]:.3f}. '
            parts += f'Missing: {escape(", ".join(missing) if missing else "none")}</p>'
        parts += '</div>'
        st.markdown(parts, unsafe_allow_html=True)

    st.markdown(f"#### Explore a possible change — {focus}")
    baseline = results[focus]
    editable = list(baseline["components"])
    lever = st.selectbox(
        "Which condition would an approved optimization change?", editable,
        format_func=lambda k: DISPLAY[k][0], key=f"lever_{portfolio}_{focus}",
    )
    before = baseline["components"][lever]
    after = st.slider(
        "Hypothetical factor level (0–100)", 0, 100, int(round(before * 100)), 1,
        key=f"whatif_{portfolio}_{focus}_{lever}",
    ) / 100
    scenario = dict(baseline["components"])
    scenario[lever] = after
    changed = calculate_score(scenario, config["weights"])
    delta = changed["score"] - baseline["score"]
    st.metric("Illustrative score after changing one factor", f"{changed['score']:.1f}/100", delta=f"{delta:+.1f} diagnostic points")
    if technical:
        st.caption(f"Only x[{lever}] changed from {before:.3f} to {after:.3f}. All other factors and weights remain fixed. This is a deterministic sensitivity demonstration, not a forecast or experimental estimate of lift.")
    else:
        st.caption("Move the slider to see how improving or weakening one condition would change the model's score. Real engagement may change differently or not at all.")

    st.markdown(f"#### Recommended edits for {focus}")
    actions = generate_recommendations(config, baseline)
    if not actions:
        st.success("No automatic edit rule fired. Manual editorial review remains essential.")
    for i, item in enumerate(actions, 1):
        st.markdown(f"**{i}. {item['action']}**")
        if technical:
            st.caption(f"Scenario priority: {item['illustrative_priority']:.2f} · Assumed effort: {item['effort_hours_assumed']}h · Evidence: {item['evidence']}")
            st.caption("Limitation: " + item["caution"])
        else:
            st.caption("Why it was suggested: " + item["evidence"])
    st.markdown("#### What happens after a change")
    if technical:
        st.write("Register the proposed asset variant, editorial sign-off, outcome measure, baseline period and confounders; use channel-permitted A/B tests where possible. Compare observed outcomes with their uncertainty. Documentation feeds create change proposals for human review and regression testing, never automatic weight changes.")
    else:
        st.write("A communications team approves the change, publishes an appropriate version, and checks whether the intended audience actually responds better. If a platform changes its guidance, the team reviews the update before changing how the engine makes recommendations.")
    st.caption("Independent candidate demonstration; uncalibrated weights and synthetic observations. Neither a verified visibility score nor endorsement by Pew.")
