"""
SRS to Cost Converter - Streamlit App
COCOMO-based project estimation from SRS documents.
"""

import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from document_parser import parse_document, ParsedDocument
from feature_extractor import extract_features
from cost_estimator import estimate_cost
from team_allocator import allocate_team
from suggestion_engine import generate_suggestions
from utils import (
    format_inr,
    format_inr_full,
    parse_duration,
    get_risk_color,
    get_complexity_color,
    calculate_confidence_level,
    generate_project_id,
)

st.set_page_config(
    page_title="SRS to Cost Converter",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.sub-title {
    text-align: center;
    color: #6b7280;
    margin-bottom: 1.8rem;
    font-size: 1.05rem;
}
.glass-card {
    background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(124,58,237,0.08));
    border: 1px solid rgba(148,163,184,0.25);
    padding: 1rem 1.2rem;
    border-radius: 16px;
    margin-bottom: 1rem;
}
.section-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1rem;
}
.small-muted {
    color: #6b7280;
    font-size: 0.9rem;
}
.kpi {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem;
}
.metric-label-custom {
    font-size: 0.85rem;
    color: #64748b;
}
.metric-value-custom {
    font-size: 1.8rem;
    font-weight: 700;
    color: #0f172a;
}
.badge {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-blue { background: #dbeafe; color: #1d4ed8; }
.badge-purple { background: #ede9fe; color: #6d28d9; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-yellow { background: #fef3c7; color: #b45309; }
.badge-red { background: #fee2e2; color: #b91c1c; }
hr {
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
}
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown('<div class="main-title">💼 SRS to Cost Converter</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Upload an SRS document and generate COCOMO-based cost, timeline, team, and delivery insights.</div>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("## ⚙️ Estimation Setup")

        uploaded_file = st.file_uploader(
            "Upload SRS Document",
            type=["pdf", "docx", "doc"],
            help="Supported formats: PDF, DOCX, DOC"
        )

        st.markdown("---")

        st.markdown("### 💰 Cost Inputs")
        cost_per_person_month = st.number_input(
            "Engineering Cost per Person-Month (₹)",
            min_value=50000,
            max_value=1000000,
            value=180000,
            step=10000,
            help="Used directly in the COCOMO cost model."
        )

        buffer_percentage = st.slider(
            "Contingency Buffer (%)",
            min_value=5,
            max_value=30,
            value=10,
            help="Additional contingency for unknowns and scope changes."
        )

        st.session_state["buffer_percentage"] = buffer_percentage   # ✅ ADD THIS LINE

        st.markdown("---")
        st.markdown("### 📌 Model")
        st.info("This app uses **COCOMO-based estimation only**.")

        if "analysis_result" in st.session_state:
            result = st.session_state.analysis_result
            st.markdown("---")
            st.markdown("### 📈 Quick Snapshot")
            st.metric("Total Cost", result["estimate"].total_cost_formatted)
            st.metric("Timeline", f'{result["estimate"].timeline_weeks} weeks')
            st.metric("Team Size", f'{result["team"].total_team_size} members')

    if uploaded_file is not None:
        process_document(uploaded_file, cost_per_person_month, buffer_percentage)
    else:
        show_welcome_page(cost_per_person_month, buffer_percentage)


def show_welcome_page(cost_per_person_month, buffer_percentage):
    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3>🚀 What this app does</h3>
            <ul>
                <li>Parses SRS documents</li>
                <li>Extracts functional features and modules</li>
                <li>Estimates project size using inferred KLOC</li>
                <li>Calculates effort, schedule, and cost using COCOMO</li>
                <li>Suggests team composition and optimization ideas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <h3>🧠 Estimation Flow</h3>
            <p class="small-muted">
                Document Parsing → Feature Extraction → Project Sizing (KLOC) → COCOMO Effort →
                Timeline → Cost Breakdown → Team Allocation → Suggestions
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-card">
            <h3>📂 Supported Formats</h3>
            <p>• PDF (.pdf)</p>
            <p>• Word (.docx, .doc)</p>
            <hr>
            <h3>✅ Best Results When SRS Includes</h3>
            <p>• Functional requirements</p>
            <p>• Modules and workflows</p>
            <p>• Integrations</p>
            <p>• Platforms and user roles</p>
            <p>• Security and performance notes</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔬 Run Sample Demo", use_container_width=True):
            show_sample_analysis(cost_per_person_month, buffer_percentage)


def process_document(uploaded_file, cost_per_person_month, buffer_percentage):
    with st.spinner("📄 Parsing document..."):
        file_content = uploaded_file.read()
        file_name = uploaded_file.name
        parsed_doc = parse_document(file_content, file_name)

    if not parsed_doc.parse_success:
        st.error(f"❌ Error parsing document: {parsed_doc.error_message}")
        return

    st.success(f"✅ Successfully parsed **{file_name}**")

    with st.expander("📄 Document Information", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pages", parsed_doc.page_count)
        c2.metric("Words", f"{parsed_doc.word_count:,}")
        c3.metric("Sections", len(parsed_doc.sections))
        c4.metric("Bullet Points", len(parsed_doc.bullet_points))

    with st.spinner("🔍 Extracting features and project signals..."):
        features = extract_features(parsed_doc)

    with st.spinner("💰 Running COCOMO estimation..."):
        estimate = estimate_cost(
            features,
            cost_per_person_month=cost_per_person_month,
            buffer_percentage=buffer_percentage
        )

    with st.spinner("👥 Allocating team..."):
        team = allocate_team(features, estimate)

    with st.spinner("💡 Generating recommendations..."):
        suggestions = generate_suggestions(features, estimate, team)

    st.session_state.analysis_result = {
        "parsed_doc": parsed_doc,
        "features": features,
        "estimate": estimate,
        "team": team,
        "suggestions": suggestions
    }

    display_results(parsed_doc, features, estimate, team, suggestions)


def display_results(parsed_doc, features, estimate, team, suggestions):
    tabs = st.tabs([
        "📊 Overview",
        "🧠 COCOMO Insights",
        "🔍 Features",
        "💰 Cost Breakdown",
        "📅 Timeline",
        "👥 Team",
        "💡 Suggestions",
        "📄 Report"
    ])

    with tabs[0]:
        display_overview(features, estimate, team)

    with tabs[1]:
        display_cocomo_insights(features, estimate)

    with tabs[2]:
        display_features(features)

    with tabs[3]:
        display_cost_breakdown(estimate)

    with tabs[4]:
        display_timeline(estimate)

    with tabs[5]:
        display_team(team)

    with tabs[6]:
        display_suggestions(suggestions)

    with tabs[7]:
        display_report(parsed_doc, features, estimate, team, suggestions)


def display_overview(features, estimate, team):
    st.subheader("📊 Executive Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estimated Cost", estimate.total_cost_formatted)
    c2.metric("Timeline", f"{estimate.timeline_weeks} weeks", delta=parse_duration(estimate.timeline_weeks))
    c3.metric("Team Size", f"{team.total_team_size} members")
    c4.metric("Confidence", calculate_confidence_level(features.extraction_confidence))

    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Features", len(features.features))
    c2.metric("Modules", len(features.modules))
    c3.metric("KLOC", f"{estimate.estimated_kloc:.1f}")
    c4.metric("Effort", f"{estimate.effort_person_months:.1f} PM")

    st.markdown("---")

    cc1, cc2 = st.columns([1.1, 1])

    with cc1:
        cost_data = pd.DataFrame({
            "Category": ["Development", "Platform", "UI", "Integration", "Testing", "Management", "Buffer"],
            "Cost": [
                estimate.cost.feature_cost,
                estimate.cost.platform_cost,
                estimate.cost.ui_cost,
                estimate.cost.integration_cost,
                estimate.cost.testing_cost,
                estimate.cost.project_management_cost,
                estimate.cost.buffer_cost
            ]
        })
        cost_data = cost_data[cost_data["Cost"] > 0]

        if not cost_data.empty:
            fig = px.pie(
                cost_data,
                values="Cost",
                names="Category",
                hole=0.55,
                title="Cost Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost distribution data available.")

    with cc2:
        phase_df = pd.DataFrame([
            {"Phase": phase.replace("_", " ").title(), "Weeks": weeks}
            for phase, weeks in estimate.timeline.phases.items()
        ])

        if not phase_df.empty:
            fig = px.bar(
                phase_df,
                x="Weeks",
                y="Phase",
                orientation="h",
                title="Timeline by Phase",
                color="Weeks",
                color_continuous_scale="Blues"
            )
            fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No phase data available.")

    st.markdown("---")

    x1, x2, x3 = st.columns(3)

    with x1:
        complexity_color = get_complexity_color(features.complexity)
        st.markdown(f"""
        <div class="kpi">
            <div class="metric-label-custom">Complexity</div>
            <div class="metric-value-custom" style="color:{complexity_color};">
                {features.complexity.replace('_', ' ').title()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with x2:
        risk_color = get_risk_color(estimate.risk_level)
        st.markdown(f"""
        <div class="kpi">
            <div class="metric-label-custom">Risk Level</div>
            <div class="metric-value-custom" style="color:{risk_color};">
                {estimate.risk_level.title()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with x3:
        st.markdown(f"""
        <div class="kpi">
            <div class="metric-label-custom">COCOMO Mode</div>
            <div class="metric-value-custom">
                {estimate.cocomo_mode.replace('_', ' ').title()}
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_cocomo_insights(features, estimate):
    st.subheader("🧠 COCOMO Model Insights")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estimated Size", f"{estimate.estimated_kloc:.2f} KLOC")
    c2.metric("Effort", f"{estimate.effort_person_months:.2f} Person-Months")
    c3.metric("COCOMO Mode", estimate.cocomo_mode.replace("_", " ").title())
    c4.metric("EAF", f"{estimate.effort_adjustment_factor:.2f}")

    st.markdown("---")

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("### 📘 Interpretation")
        st.markdown(f"""
        - **Estimated KLOC:** {estimate.estimated_kloc:.2f}
        - **Effort:** {estimate.effort_person_months:.2f} person-months
        - **Schedule:** {estimate.timeline.total_months:.2f} months
        - **Risk Level:** {estimate.risk_level.title()}
        - **Complexity:** {features.complexity.replace('_', ' ').title()}
        """)

        if estimate.risk_factors:
            st.markdown("### ⚠️ Key Risk Factors")
            for factor in estimate.risk_factors:
                st.warning(factor)
        else:
            st.success("No major risk factors identified.")

    with right:
        breakdown_df = pd.DataFrame({
            "Metric": ["KLOC", "Effort (PM)", "Schedule (Months)", "Buffer (%)"],
            "Value": [
                estimate.estimated_kloc,
                estimate.effort_person_months,
                estimate.timeline.total_months,
                st.session_state.get("buffer_percentage", 10)
            ]
        })

        fig = px.bar(
            breakdown_df,
            x="Metric",
            y="Value",
            title="COCOMO Estimation Signals",
            color="Metric",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def display_features(features):
    st.subheader("🔍 Extracted Features")

    c1, c2, c3, c4 = st.columns(4)
    feature_complexities = [f.get("complexity", "medium") for f in features.features]
    c1.metric("Total Features", len(features.features))
    c2.metric("High", feature_complexities.count("high"))
    c3.metric("Medium", feature_complexities.count("medium"))
    c4.metric("Low", feature_complexities.count("low"))

    st.markdown("---")

    col1, col2 = st.columns([2.2, 1])

    with col1:
        complexity_filter = st.multiselect(
            "Filter by Complexity",
            options=["low", "medium", "high"],
            default=["low", "medium", "high"]
        )

        if features.features:
            for i, feature in enumerate(features.features):
                complexity = feature.get("complexity", "medium")
                if complexity not in complexity_filter:
                    continue

                with st.expander(f"Feature {i+1}: {feature['description'][:70]}"):
                    st.write(f"**Description:** {feature['description']}")
                    st.write(f"**Complexity:** {complexity.title()}")
                    st.write(f"**Source:** {feature.get('source', 'unknown').replace('_', ' ').title()}")
        else:
            st.info("No features extracted.")

    with col2:
        st.markdown("### 📦 Modules")
        if features.modules:
            for module in features.modules:
                st.markdown(f"- {module}")
        else:
            st.info("No modules detected")

        st.markdown("### 👤 User Roles")
        if features.user_roles:
            for role in features.user_roles:
                st.markdown(f"- {role}")
        else:
            st.info("No user roles detected")

        st.markdown("### 🔧 Technologies")
        if features.key_technologies:
            for tech in features.key_technologies:
                st.markdown(f"- {tech}")
        else:
            st.info("No technologies detected")


def display_cost_breakdown(estimate):
    st.subheader("💰 Cost Breakdown")

    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label-custom">Total Estimated Cost</div>
        <div class="metric-value-custom">{estimate.total_cost_formatted}</div>
        <div class="small-muted">{format_inr_full(estimate.total_cost_inr)}</div>
    </div>
    """, unsafe_allow_html=True)

    data = [
        ("Development", estimate.cost.feature_cost),
        ("Platform", estimate.cost.platform_cost),
        ("UI", estimate.cost.ui_cost),
        ("Integration", estimate.cost.integration_cost),
        ("Testing & QA", estimate.cost.testing_cost),
        ("Project Management", estimate.cost.project_management_cost),
        ("Buffer", estimate.cost.buffer_cost),
    ]

    df = pd.DataFrame(data, columns=["Component", "Cost"])
    df["Share"] = df["Cost"].apply(lambda x: (x / estimate.total_cost_inr * 100) if estimate.total_cost_inr else 0)

    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.dataframe(df.style.format({"Cost": lambda x: format_inr(x), "Share": "{:.1f}%"}), use_container_width=True)

    with col2:
        fig = px.bar(
            df,
            x="Component",
            y="Cost",
            color="Cost",
            title="Cost Components",
            color_continuous_scale="Purples"
        )
        fig.update_layout(xaxis_title="", yaxis_title="Cost (₹)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Cost / Feature", format_inr(estimate.cost.cost_per_feature))
    c2.metric("Cost / Module", format_inr(estimate.cost.cost_per_module))
    c3.metric("Complexity Multiplier", f"x{estimate.cost.complexity_multiplier:.2f}")

    if estimate.cost.integration_breakdown:
        st.markdown("---")
        st.markdown("### 🔗 Integration Cost Distribution")

        integration_df = pd.DataFrame(estimate.cost.integration_breakdown)
        fig = px.bar(
            integration_df,
            x="cost",
            y="name",
            orientation="h",
            title="Integration Breakdown",
            color="cost",
            color_continuous_scale="Blues"
        )
        fig.update_layout(xaxis_title="Cost (₹)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📅 Phase-wise Cost Allocation")
    phase_df = pd.DataFrame([
        {"Phase": phase.replace("_", " ").title(), "Cost": cost}
        for phase, cost in estimate.cost.phase_breakdown.items()
    ])

    fig = px.bar(
        phase_df,
        x="Phase",
        y="Cost",
        color="Cost",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)


def display_timeline(estimate):
    st.subheader("📅 Delivery Timeline")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Duration", f"{estimate.timeline.total_weeks} weeks")
    c2.metric("Working Days", estimate.timeline.total_days)
    c3.metric("Start", estimate.timeline.estimated_start)
    c4.metric("End", estimate.timeline.estimated_end)

    st.markdown("---")

    phase_df = pd.DataFrame([
        {"Phase": phase.replace("_", " ").title(), "Weeks": weeks}
        for phase, weeks in estimate.timeline.phases.items()
    ])

    if not phase_df.empty:
        fig = px.bar(
            phase_df,
            x="Weeks",
            y="Phase",
            orientation="h",
            title="Phase Timeline",
            color="Weeks",
            color_continuous_scale="Tealgrn"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏁 Milestones")
    left, right = st.columns(2)

    for i, milestone in enumerate(estimate.timeline.milestones):
        target_col = left if i % 2 == 0 else right
        with target_col:
            st.markdown(f"""
            <div class="section-card" style="margin-bottom: 0.75rem;">
                <strong>Week {milestone['week']}</strong><br>
                {milestone['name']}<br>
                <span class="small-muted">{milestone['description']}</span>
            </div>
            """, unsafe_allow_html=True)


def display_team(team):
    st.subheader("👥 Recommended Team Composition")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Team", team.total_team_size)
    c2.metric("Developers", team.developers)
    c3.metric("Designers", team.designers)
    c4.metric("Testers", team.testers)
    c5.metric("Others", team.managers + team.specialists)

    st.markdown("---")

    col1, col2 = st.columns([1.7, 1])

    with col1:
        if team.team_members:
            for member in team.team_members:
                with st.expander(f"{member.role} ({member.count})", expanded=True):
                    x1, x2, x3 = st.columns(3)
                    x1.metric("Count", member.count)
                    x2.metric("Duration", f"{member.total_weeks} weeks")
                    x3.metric("Cost", format_inr(member.total_cost))

                    st.markdown("**Responsibilities**")
                    for r in member.responsibilities:
                        st.markdown(f"- {r}")
        else:
            st.info("No team recommendations available.")

    with col2:
        if team.team_members:
            team_df = pd.DataFrame([{"Role": m.role, "Count": m.count} for m in team.team_members])
            fig = px.pie(
                team_df,
                names="Role",
                values="Count",
                hole=0.5,
                title="Team Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No team distribution to display.")

        st.markdown("### 🎯 Required Skills")
        if team.required_skills:
            for skill in team.required_skills[:12]:
                st.markdown(f"- {skill}")
        else:
            st.info("No skills inferred.")

    if team.recommendations:
        st.markdown("---")
        st.markdown("### 💡 Team Recommendations")
        for rec in team.recommendations:
            st.info(rec)


def display_suggestions(suggestions):
    st.subheader("💡 Recommendations & Optimization")

    if suggestions.total_potential_savings > 0:
        st.success(f"Potential savings if optimized well: **{suggestions.total_potential_savings_formatted}**")

    tabs = st.tabs([
        "Cost Reduction",
        "Risk Mitigation",
        "Timeline Optimization",
        "Quality Improvement",
        "Complexity Warnings"
    ])

    with tabs[0]:
        if suggestions.cost_reduction:
            for s in suggestions.cost_reduction:
                with st.expander(f"💰 {s.title}", expanded=True):
                    st.write(f"**Category:** {s.category}")
                    st.write(f"**Description:** {s.description}")
                    if s.potential_saving > 0:
                        st.write(f"**Potential Saving:** {s.potential_saving_formatted}")
                    st.write(f"**Priority:** {s.priority.title()}")
                    st.write(f"**Effort:** {s.implementation_effort.title()}")
        else:
            st.info("No cost reduction suggestions available.")

    with tabs[1]:
        if suggestions.risk_mitigation:
            for s in suggestions.risk_mitigation:
                with st.expander(f"⚠️ {s.title}", expanded=True):
                    st.write(f"**Category:** {s.category}")
                    st.write(f"**Description:** {s.description}")
                    st.write(f"**Priority:** {s.priority.title()}")
        else:
            st.success("No major mitigation recommendations.")

    with tabs[2]:
        if suggestions.timeline_optimization:
            for s in suggestions.timeline_optimization:
                with st.expander(f"⏱️ {s.title}", expanded=True):
                    st.write(f"**Category:** {s.category}")
                    st.write(f"**Description:** {s.description}")
                    st.write(f"**Priority:** {s.priority.title()}")
        else:
            st.info("No timeline optimization suggestions.")

    with tabs[3]:
        if suggestions.quality_improvement:
            for s in suggestions.quality_improvement:
                with st.expander(f"✅ {s.title}", expanded=True):
                    st.write(f"**Category:** {s.category}")
                    st.write(f"**Description:** {s.description}")
                    st.write(f"**Priority:** {s.priority.title()}")
        else:
            st.info("No quality suggestions available.")

    with tabs[4]:
        if suggestions.complexity_warnings:
            for warning in suggestions.complexity_warnings:
                st.warning(
                    f"#{warning['id']} - {warning['text']}\n\n"
                    f"Reason: {warning['reason']}\n\n"
                    f"Recommendation: {warning['recommendation']}"
                )
        else:
            st.success("No major complexity warnings.")


def display_report(parsed_doc, features, estimate, team, suggestions):
    st.subheader("📄 Exportable Project Report")

    project_id = generate_project_id()

    st.markdown(f"""
    <div class="section-card">
        <h3>Project Estimation Summary</h3>
        <p><strong>Project ID:</strong> {project_id}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Document:</strong> {parsed_doc.file_name}</p>
    </div>
    """, unsafe_allow_html=True)

    summary_df = pd.DataFrame([
        ("Estimated Cost", estimate.total_cost_formatted),
        ("Timeline", f"{estimate.timeline_weeks} weeks"),
        ("Team Size", team.total_team_size),
        ("Features", len(features.features)),
        ("Modules", len(features.modules)),
        ("Complexity", features.complexity.replace("_", " ").title()),
        ("Risk Level", estimate.risk_level.title()),
        ("COCOMO Mode", estimate.cocomo_mode.replace("_", " ").title()),
        ("Estimated KLOC", f"{estimate.estimated_kloc:.2f}"),
        ("Effort (PM)", f"{estimate.effort_person_months:.2f}")
    ], columns=["Parameter", "Value"])

    st.dataframe(summary_df, use_container_width=True)

    st.markdown("### 📥 Export")
    c1, c2 = st.columns(2)

    report_data = {
        "project_id": project_id,
        "generated_at": datetime.now().isoformat(),
        "document": parsed_doc.file_name,
        "summary": {
            "total_cost": estimate.total_cost_inr,
            "total_cost_formatted": estimate.total_cost_formatted,
            "timeline_weeks": estimate.timeline_weeks,
            "team_size": team.total_team_size,
            "features_count": len(features.features),
            "modules_count": len(features.modules),
            "complexity": features.complexity,
            "risk_level": estimate.risk_level,
            "cocomo_mode": estimate.cocomo_mode,
            "estimated_kloc": estimate.estimated_kloc,
            "effort_person_months": estimate.effort_person_months,
            "eaf": estimate.effort_adjustment_factor
        },
        "features": [f["description"] for f in features.features],
        "modules": features.modules,
        "integrations": features.integrations,
        "cost_breakdown": {
            "feature_cost": estimate.cost.feature_cost,
            "platform_cost": estimate.cost.platform_cost,
            "ui_cost": estimate.cost.ui_cost,
            "integration_cost": estimate.cost.integration_cost,
            "testing_cost": estimate.cost.testing_cost,
            "pm_cost": estimate.cost.project_management_cost,
            "buffer_cost": estimate.cost.buffer_cost,
            "total_cost": estimate.total_cost_inr
        },
        "timeline": {
            "start_date": estimate.timeline.estimated_start,
            "end_date": estimate.timeline.estimated_end,
            "phases": estimate.timeline.phases,
            "milestones": estimate.timeline.milestones
        },
        "team": [
            {
                "role": m.role,
                "count": m.count,
                "weekly_rate": m.weekly_rate,
                "total_weeks": m.total_weeks,
                "cost": m.total_cost
            }
            for m in team.team_members
        ],
        "suggestions": {
            "potential_savings": suggestions.total_potential_savings,
            "cost_reduction_count": len(suggestions.cost_reduction),
            "risk_mitigation_count": len(suggestions.risk_mitigation),
            "timeline_optimization_count": len(suggestions.timeline_optimization),
            "quality_improvement_count": len(suggestions.quality_improvement)
        }
    }

    json_str = json.dumps(report_data, indent=2)

    with c1:
        st.download_button(
            label="📥 Download JSON Report",
            data=json_str,
            file_name=f"srs_cocomo_report_{project_id}.json",
            mime="application/json",
            use_container_width=True
        )

    with c2:
        csv_data = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary CSV",
            data=csv_data,
            file_name=f"srs_cocomo_summary_{project_id}.csv",
            mime="text/csv",
            use_container_width=True
        )


def show_sample_analysis(cost_per_person_month, buffer_percentage):
    st.info("Showing demo analysis using sample SRS data...")

    sample_doc = ParsedDocument(
        raw_text="""
        Sample E-Commerce Platform SRS

        The system shall allow users to browse products.
        The system shall implement shopping cart functionality.
        Users should be able to make payments via online payment gateways.
        The application shall support push notifications.
        The system shall have an admin dashboard for management.
        Integration with SMS gateway for OTP verification.
        Real-time chat support for customers.
        The platform shall be available on web and mobile.
        The system should provide analytics dashboards for administrators.
        The system must support secure authentication and authorization.
        """,
        file_name="sample_srs.pdf",
        word_count=120,
        page_count=5,
        parse_success=True
    )

    features = extract_features(sample_doc)
    estimate = estimate_cost(
        features,
        cost_per_person_month=cost_per_person_month,
        buffer_percentage=buffer_percentage
    )
    team = allocate_team(features, estimate)
    suggestions = generate_suggestions(features, estimate, team)

    st.session_state.analysis_result = {
        "parsed_doc": sample_doc,
        "features": features,
        "estimate": estimate,
        "team": team,
        "suggestions": suggestions
    }

    display_results(sample_doc, features, estimate, team, suggestions)


if __name__ == "__main__":
    main()