"""
SRS Document Analyzer - Main Streamlit Application
An intelligent application that analyzes SRS documents and estimates project costs.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import io
import json

# Import custom modules
from document_parser import parse_document, ParsedDocument
from feature_extractor import extract_features, ExtractedFeatures
from cost_estimator import estimate_cost, ProjectEstimate
from team_allocator import allocate_team, TeamAllocation
from suggestion_engine import generate_suggestions, ProjectSuggestions
from utils import (
    format_inr, format_inr_full, parse_duration, 
    get_risk_color, get_complexity_color, calculate_confidence_level,
    generate_project_id, export_to_json
)

# Page configuration
st.set_page_config(
    page_title="SRS Document Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .feature-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
    }
    .complexity-low { color: #28a745; }
    .complexity-medium { color: #17a2b8; }
    .complexity-high { color: #ffc107; }
    .complexity-very_high { color: #dc3545; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 SRS Document Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Project Cost & Timeline Estimation</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Document")
        uploaded_file = st.file_uploader(
            "Upload your SRS document",
            type=['pdf', 'docx', 'doc'],
            help="Supported formats: PDF, Word (docx, doc)"
        )
        
        st.markdown("---")
        
        # Configuration options
        st.header("⚙️ Configuration")
        
        base_cost = st.number_input(
            "Base Cost per Feature (₹)",
            min_value=5000,
            max_value=50000,
            value=10000,
            step=1000
        )
        
        buffer_percentage = st.slider(
            "Buffer Percentage",
            min_value=5,
            max_value=30,
            value=10,
            help="Additional buffer for unforeseen requirements"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.header("📈 Quick Stats")
        if 'analysis_result' in st.session_state:
            result = st.session_state.analysis_result
            st.metric("Total Cost", result['estimate'].total_cost_formatted)
            st.metric("Timeline", f"{result['estimate'].timeline_weeks} weeks")
            st.metric("Team Size", f"{result['team'].total_team_size} members")
    
    # Main content area
    if uploaded_file is not None:
        process_document(uploaded_file, base_cost, buffer_percentage)
    else:
        show_welcome_page()


def show_welcome_page():
    """Display welcome page with instructions"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🚀 Welcome to SRS Document Analyzer
        
        This intelligent application helps you:
        
        - 📄 **Parse** Software Requirement Specification documents
        - 🔍 **Extract** features, modules, and complexity indicators
        - 💰 **Estimate** project costs with detailed breakdowns
        - 📅 **Plan** timelines and milestones
        - 👥 **Allocate** optimal team composition
        - 💡 **Suggest** cost optimizations and risk mitigations
        
        ### How to Use
        
        1. **Upload** your SRS document (PDF or Word format)
        2. **Review** the extracted features and parameters
        3. **Analyze** the cost breakdown and timeline
        4. **Explore** suggestions for optimization
        
        ### Supported Document Formats
        
        - PDF (.pdf)
        - Microsoft Word (.docx, .doc)
        
        ---
        
        📁 **Upload a document from the sidebar to get started!**
        """)
        
        # Sample analysis button
        if st.button("🔬 Try with Sample Data"):
            show_sample_analysis()


def process_document(uploaded_file, base_cost, buffer_percentage):
    """Process uploaded document and display results"""
    
    with st.spinner("📄 Parsing document..."):
        # Read file content
        file_content = uploaded_file.read()
        file_name = uploaded_file.name
        
        # Parse document
        parsed_doc = parse_document(file_content, file_name)
    
    if not parsed_doc.parse_success:
        st.error(f"❌ Error parsing document: {parsed_doc.error_message}")
        return
    
    # Show parsing success
    st.success(f"✅ Successfully parsed: {file_name}")
    
    # Display document info
    with st.expander("📄 Document Information", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Pages", parsed_doc.page_count)
        col2.metric("Words", f"{parsed_doc.word_count:,}")
        col3.metric("Sections", len(parsed_doc.sections))
        col4.metric("Bullet Points", len(parsed_doc.bullet_points))
    
    # Extract features
    with st.spinner("🔍 Extracting features and analyzing complexity..."):
        features = extract_features(parsed_doc)
    
    # Estimate costs
    with st.spinner("💰 Calculating project costs..."):
        estimate = estimate_cost(features)
    
    # Allocate team
    with st.spinner("👥 Determining optimal team composition..."):
        team = allocate_team(features, estimate)
    
    # Generate suggestions
    with st.spinner("💡 Generating intelligent suggestions..."):
        suggestions = generate_suggestions(features, estimate, team)
    
    # Store results in session state
    st.session_state.analysis_result = {
        'parsed_doc': parsed_doc,
        'features': features,
        'estimate': estimate,
        'team': team,
        'suggestions': suggestions
    }
    
    # Display results
    display_results(parsed_doc, features, estimate, team, suggestions)


def display_results(parsed_doc, features, estimate, team, suggestions):
    """Display analysis results"""
    
    # Create tabs for different sections
    tabs = st.tabs([
        "📊 Overview",
        "🔍 Features",
        "💰 Cost Breakdown",
        "📅 Timeline",
        "👥 Team",
        "💡 Suggestions",
        "📄 Report"
    ])
    
    # Tab 1: Overview
    with tabs[0]:
        display_overview(features, estimate, team, suggestions)
    
    # Tab 2: Features
    with tabs[1]:
        display_features(features)
    
    # Tab 3: Cost Breakdown
    with tabs[2]:
        display_cost_breakdown(estimate)
    
    # Tab 4: Timeline
    with tabs[3]:
        display_timeline(estimate)
    
    # Tab 5: Team
    with tabs[4]:
        display_team(team)
    
    # Tab 6: Suggestions
    with tabs[5]:
        display_suggestions(suggestions)
    
    # Tab 7: Report
    with tabs[6]:
        display_report(parsed_doc, features, estimate, team, suggestions)


def display_overview(features, estimate, team, suggestions):
    """Display overview dashboard"""
    
    st.header("📊 Project Overview")
    
    # Key Metrics Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Estimated Cost",
            value=estimate.total_cost_formatted,
            help="Total estimated project cost in INR"
        )
    
    with col2:
        st.metric(
            label="📅 Timeline",
            value=f"{estimate.timeline_weeks} weeks",
            delta=parse_duration(estimate.timeline_weeks)
        )
    
    with col3:
        st.metric(
            label="👥 Team Size",
            value=f"{team.total_team_size} members",
            help="Recommended team composition"
        )
    
    with col4:
        confidence = calculate_confidence_level(features.extraction_confidence)
        st.metric(
            label="🎯 Confidence",
            value=confidence,
            help="Estimation confidence based on document quality"
        )
    
    st.markdown("---")
    
    # Key Metrics Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔧 Features",
            value=len(features.features),
            help="Number of features extracted"
        )
    
    with col2:
        st.metric(
            label="📦 Modules",
            value=len(features.modules),
            help="Number of modules identified"
        )
    
    with col3:
        complexity_color = get_complexity_color(features.complexity)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Complexity Level</div>
            <div class="metric-value" style="color: {complexity_color}">
                {features.complexity.upper().replace('_', ' ')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_color = get_risk_color(estimate.risk_level)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Risk Level</div>
            <div class="metric-value" style="color: {risk_color}">
                {estimate.risk_level.upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost Distribution Pie Chart
        cost_data = {
            'Category': ['Features', 'Platform', 'UI', 'Integration', 'Testing', 'Management', 'Buffer'],
            'Cost': [
                estimate.cost.feature_cost,
                estimate.cost.platform_cost,
                estimate.cost.ui_cost,
                estimate.cost.integration_cost,
                estimate.cost.testing_cost,
                estimate.cost.project_management_cost,
                estimate.cost.buffer_cost
            ]
        }
        df_cost = pd.DataFrame(cost_data)
        df_cost = df_cost[df_cost['Cost'] > 0]
        
        fig = px.pie(
            df_cost,
            values='Cost',
            names='Category',
            title='Cost Distribution',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Timeline Gantt-style Chart
        phases = list(estimate.timeline.phases.keys())
        durations = list(estimate.timeline.phases.values())
        
        # Calculate start weeks
        start_weeks = [0]
        for i in range(len(durations) - 1):
            start_weeks.append(start_weeks[-1] + durations[i])
        
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set2
        for i, (phase, duration, start) in enumerate(zip(phases, durations, start_weeks)):
            fig.add_trace(go.Bar(
                y=[phase.replace('_', ' ').title()],
                x=[duration],
                orientation='h',
                marker_color=colors[i % len(colors)],
                text=f'{duration}w',
                textposition='inside',
                name=phase.replace('_', ' ').title()
            ))
        
        fig.update_layout(
            title='Development Phases',
            xaxis_title='Weeks',
            barmode='stack',
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Platform and Integration Summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖥️ Platform")
        platform_display = features.platform.replace('_', ' ').title()
        st.info(f"**Target Platform:** {platform_display}")
        
        if features.platform_details.get('matches'):
            st.write("**Detected Keywords:**")
            for platform, keywords in features.platform_details['matches'].items():
                st.write(f"- {platform.replace('_', ' ').title()}: {', '.join(keywords[:3])}")
    
    with col2:
        st.subheader("🔗 Integrations")
        if features.integrations:
            for integration in features.integrations:
                st.markdown(f"• {integration.replace('_', ' ').title()}")
        else:
            st.info("No specific integrations detected")


def display_features(features):
    """Display extracted features"""
    
    st.header("🔍 Extracted Features")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    feature_complexities = [f.get('complexity', 'medium') for f in features.features]
    
    col1.metric("Total Features", len(features.features))
    col2.metric("High Complexity", feature_complexities.count('high'))
    col3.metric("Medium Complexity", feature_complexities.count('medium'))
    col4.metric("Low Complexity", feature_complexities.count('low'))
    
    st.markdown("---")
    
    # Feature list
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Feature List")
        
        # Filter options
        complexity_filter = st.multiselect(
            "Filter by Complexity",
            options=['low', 'medium', 'high'],
            default=['low', 'medium', 'high']
        )
        
        for i, feature in enumerate(features.features):
            complexity = feature.get('complexity', 'medium')
            
            if complexity not in complexity_filter:
                continue
            
            complexity_class = f"complexity-{complexity}"
            source = feature.get('source', 'unknown')
            
            with st.expander(f"Feature {i+1}: {feature['description'][:60]}..."):
                st.markdown(f"**Description:** {feature['description']}")
                st.markdown(f"**Complexity:** <span class='{complexity_class}'>{complexity.upper()}</span>", 
                           unsafe_allow_html=True)
                st.markdown(f"**Source:** {source.replace('_', ' ').title()}")
    
    with col2:
        st.subheader("📦 Modules")
        
        if features.modules:
            for module in features.modules:
                st.markdown(f"• {module}")
        else:
            st.info("No specific modules detected")
        
        st.markdown("---")
        
        st.subheader("👤 User Roles")
        
        if features.user_roles:
            for role in features.user_roles:
                st.markdown(f"• {role}")
        else:
            st.info("No specific user roles detected")
        
        st.markdown("---")
        
        st.subheader("🔧 Technologies")
        
        if features.key_technologies:
            for tech in features.key_technologies:
                st.markdown(f"• {tech}")
        else:
            st.info("No specific technologies mentioned")


def display_cost_breakdown(estimate):
    """Display detailed cost breakdown"""
    
    st.header("💰 Cost Breakdown")
    
    # Total cost prominently displayed
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px;">
        <h2 style="color: #666;">Total Estimated Cost</h2>
        <h1 style="color: #1f77b4; font-size: 3rem;">{estimate.total_cost_formatted}</h1>
        <p style="color: #888;">({format_inr_full(estimate.total_cost_inr)})</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Cost breakdown table
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Cost Components")
        
        cost_items = [
            ("Base Feature Cost", estimate.cost.feature_cost),
            ("Platform Adjustment", estimate.cost.platform_cost),
            ("UI Complexity Adjustment", estimate.cost.ui_cost),
            ("Integration Costs", estimate.cost.integration_cost),
            ("Testing & QA", estimate.cost.testing_cost),
            ("Project Management", estimate.cost.project_management_cost),
            ("Buffer/Contingency", estimate.cost.buffer_cost),
        ]
        
        for item, cost in cost_items:
            percentage = (cost / estimate.total_cost_inr) * 100 if estimate.total_cost_inr > 0 else 0
            col_a, col_b, col_c = st.columns([3, 2, 1])
            col_a.write(item)
            col_b.write(format_inr(cost))
            col_c.write(f"{percentage:.1f}%")
    
    with col2:
        st.subheader("⚙️ Multipliers Applied")
        
        st.markdown(f"""
        | Multiplier | Value |
        |------------|-------|
        | Complexity | ×{estimate.cost.complexity_multiplier:.2f} |
        | Platform | ×{estimate.cost.platform_multiplier:.2f} |
        | UI Complexity | ×{estimate.cost.ui_multiplier:.2f} |
        """)
        
        st.markdown("---")
        
        st.subheader("📈 Per-Unit Costs")
        st.metric("Cost per Feature", format_inr(estimate.cost.cost_per_feature))
        st.metric("Cost per Module", format_inr(estimate.cost.cost_per_module))
    
    st.markdown("---")
    
    # Integration costs breakdown
    if estimate.cost.integration_breakdown:
        st.subheader("🔗 Integration Costs")
        
        integration_df = pd.DataFrame(estimate.cost.integration_breakdown)
        integration_df['cost_formatted'] = integration_df['cost'].apply(format_inr)
        
        # Create a horizontal bar chart
        fig = px.bar(
            integration_df,
            y='name',
            x='cost',
            orientation='h',
            title='Integration Costs Breakdown',
            labels={'cost': 'Cost (₹)', 'name': 'Integration'},
            color='cost',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Phase-wise cost breakdown
    st.subheader("📅 Phase-wise Cost Distribution")
    
    phase_data = pd.DataFrame([
        {'Phase': phase.replace('_', ' ').title(), 'Cost': cost}
        for phase, cost in estimate.cost.phase_breakdown.items()
    ])
    
    fig = px.bar(
        phase_data,
        x='Phase',
        y='Cost',
        title='Cost by Development Phase',
        color='Cost',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)


def display_timeline(estimate):
    """Display timeline and milestones"""
    
    st.header("📅 Project Timeline")
    
    # Timeline summary
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Duration", f"{estimate.timeline.total_weeks} weeks")
    col2.metric("Working Days", estimate.timeline.total_days)
    col3.metric("Start Date", estimate.timeline.estimated_start)
    col4.metric("End Date", estimate.timeline.estimated_end)
    
    st.markdown("---")
    
    # Gantt-style timeline
    st.subheader("🗓️ Development Phases")
    
    # Create timeline data
    phases = []
    current_week = 0
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, (phase, weeks) in enumerate(estimate.timeline.phases.items()):
        phases.append({
            'Phase': phase.replace('_', ' ').title(),
            'Start': current_week,
            'End': current_week + weeks,
            'Duration': weeks,
            'Color': colors[i % len(colors)]
        })
        current_week += weeks
    
    # Create Gantt chart
    fig = go.Figure()
    
    for phase in phases:
        fig.add_trace(go.Bar(
            y=[phase['Phase']],
            x=[phase['Duration']],
            orientation='h',
            marker_color=phase['Color'],
            text=f"{phase['Duration']} weeks",
            textposition='inside',
            hoverinfo='text',
            hovertext=f"{phase['Phase']}: Week {phase['Start']+1} to Week {phase['End']}"
        ))
    
    fig.update_layout(
        title='Project Timeline (Weeks)',
        xaxis_title='Weeks',
        barmode='stack',
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Milestones
    st.subheader("🏁 Key Milestones")
    
    milestone_col1, milestone_col2 = st.columns(2)
    
    for i, milestone in enumerate(estimate.timeline.milestones):
        col = milestone_col1 if i % 2 == 0 else milestone_col2
        with col:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; 
                        border-left: 4px solid #1f77b4; margin-bottom: 1rem;">
                <strong>Week {milestone['week']}</strong><br>
                {milestone['name']}<br>
                <small style="color: #666;">{milestone['description']}</small>
            </div>
            """, unsafe_allow_html=True)


def display_team(team):
    """Display team allocation"""
    
    st.header("👥 Team Composition")
    
    # Team size summary
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Team", team.total_team_size)
    col2.metric("Developers", team.developers)
    col3.metric("Designers", team.designers)
    col4.metric("Testers", team.testers)
    col5.metric("Others", team.managers + team.specialists)
    
    st.markdown("---")
    
    # Team breakdown
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🧑‍💻 Team Members")
        
        for member in team.team_members:
            with st.expander(f"{member.role} ({member.count})", expanded=True):
                cols = st.columns([1, 1, 1])
                cols[0].metric("Count", member.count)
                cols[1].metric("Duration", f"{member.total_weeks} weeks")
                cols[2].metric("Cost", format_inr(member.total_cost))
                
                st.markdown("**Responsibilities:**")
                for resp in member.responsibilities:
                    st.markdown(f"• {resp}")
    
    with col2:
        # Team composition pie chart
        team_data = pd.DataFrame([
            {'Role': m.role, 'Count': m.count}
            for m in team.team_members
        ])
        
        fig = px.pie(
            team_data,
            values='Count',
            names='Role',
            title='Team Distribution',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Required skills
        st.subheader("🎯 Required Skills")
        for skill in team.required_skills[:10]:
            st.markdown(f"• {skill}")
    
    # Recommendations
    if team.recommendations:
        st.markdown("---")
        st.subheader("💡 Team Recommendations")
        
        for rec in team.recommendations:
            st.info(rec)


def display_suggestions(suggestions):
    """Display intelligent suggestions"""
    
    st.header("💡 Intelligent Suggestions")
    
    # Potential savings summary
    if suggestions.total_potential_savings > 0:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background-color: #d4edda; 
                    border-radius: 10px; margin-bottom: 2rem;">
            <h3 style="color: #155724;">💰 Potential Savings</h3>
            <h2 style="color: #155724;">{suggestions.total_potential_savings_formatted}</h2>
            <p style="color: #155724;">If all cost reduction suggestions are implemented</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for different suggestion categories
    suggestion_tabs = st.tabs([
        "💰 Cost Reduction",
        "⚠️ Risk Mitigation",
        "⏱️ Timeline Optimization",
        "✅ Quality Improvement",
        "🔴 Complexity Warnings"
    ])
    
    with suggestion_tabs[0]:
        st.subheader("Cost Reduction Suggestions")
        if suggestions.cost_reduction:
            for sugg in suggestions.cost_reduction:
                with st.expander(f"💡 {sugg.title}", expanded=True):
                    st.markdown(f"**Category:** {sugg.category}")
                    st.markdown(f"**Description:** {sugg.description}")
                    if sugg.potential_saving > 0:
                        st.markdown(f"**Potential Saving:** {sugg.potential_saving_formatted}")
                    st.markdown(f"**Priority:** {sugg.priority.upper()}")
                    st.markdown(f"**Implementation Effort:** {sugg.implementation_effort.title()}")
        else:
            st.info("No cost reduction suggestions at this time")
    
    with suggestion_tabs[1]:
        st.subheader("Risk Mitigation Suggestions")
        if suggestions.risk_mitigation:
            for sugg in suggestions.risk_mitigation:
                with st.expander(f"⚠️ {sugg.title}", expanded=True):
                    st.markdown(f"**Category:** {sugg.category}")
                    st.markdown(f"**Description:** {sugg.description}")
                    st.markdown(f"**Priority:** {sugg.priority.upper()}")
        else:
            st.success("No significant risks identified")
    
    with suggestion_tabs[2]:
        st.subheader("Timeline Optimization Suggestions")
        if suggestions.timeline_optimization:
            for sugg in suggestions.timeline_optimization:
                with st.expander(f"⏱️ {sugg.title}", expanded=True):
                    st.markdown(f"**Category:** {sugg.category}")
                    st.markdown(f"**Description:** {sugg.description}")
                    st.markdown(f"**Priority:** {sugg.priority.upper()}")
        else:
            st.info("Timeline is already optimized")
    
    with suggestion_tabs[3]:
        st.subheader("Quality Improvement Suggestions")
        if suggestions.quality_improvement:
            for sugg in suggestions.quality_improvement:
                with st.expander(f"✅ {sugg.title}", expanded=True):
                    st.markdown(f"**Category:** {sugg.category}")
                    st.markdown(f"**Description:** {sugg.description}")
                    st.markdown(f"**Priority:** {sugg.priority.upper()}")
        else:
            st.info("No quality improvement suggestions at this time")
    
    with suggestion_tabs[4]:
        st.subheader("Complexity Warnings")
        if suggestions.complexity_warnings:
            for warning in suggestions.complexity_warnings:
                st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 1rem; border-radius: 5px; 
                            border-left: 4px solid #ffc107; margin-bottom: 1rem;">
                    <strong>⚠️ Warning #{warning['id']}</strong><br>
                    <p>{warning['text']}</p>
                    <small><strong>Reason:</strong> {warning['reason']}</small><br>
                    <small><strong>Recommendation:</strong> {warning['recommendation']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No high complexity warnings")


def display_report(parsed_doc, features, estimate, team, suggestions):
    """Display and export report"""
    
    st.header("📄 Project Report")
    
    # Generate project ID
    project_id = generate_project_id()
    
    # Report summary
    st.markdown(f"""
    ## Project Estimation Report
    
    **Project ID:** {project_id}  
    **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    **Document:** {parsed_doc.file_name}
    
    ---
    
    ### Executive Summary
    
    | Parameter | Value |
    |-----------|-------|
    | Estimated Cost | {estimate.total_cost_formatted} |
    | Timeline | {estimate.timeline_weeks} weeks |
    | Team Size | {team.total_team_size} members |
    | Features | {len(features.features)} |
    | Complexity | {features.complexity.replace('_', ' ').title()} |
    | Risk Level | {estimate.risk_level.title()} |
    
    ---
    
    ### Cost Breakdown
    
    | Component | Amount |
    |-----------|--------|
    | Feature Development | {format_inr(estimate.cost.feature_cost)} |
    | Platform Adjustment | {format_inr(estimate.cost.platform_cost)} |
    | UI Complexity | {format_inr(estimate.cost.ui_cost)} |
    | Integrations | {format_inr(estimate.cost.integration_cost)} |
    | Testing & QA | {format_inr(estimate.cost.testing_cost)} |
    | Project Management | {format_inr(estimate.cost.project_management_cost)} |
    | Buffer | {format_inr(estimate.cost.buffer_cost)} |
    | **Total** | **{estimate.total_cost_formatted}** |
    
    ---
    
    ### Timeline
    
    - **Start Date:** {estimate.timeline.estimated_start}
    - **End Date:** {estimate.timeline.estimated_end}
    - **Total Duration:** {estimate.timeline_weeks} weeks ({estimate.timeline.total_days} working days)
    
    ---
    
    ### Potential Savings
    
    If all optimization suggestions are implemented:  
    **Potential Savings:** {suggestions.total_potential_savings_formatted}
    
    """)
    
    # Export options
    st.markdown("---")
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        report_data = {
            'project_id': project_id,
            'generated_at': datetime.now().isoformat(),
            'document': parsed_doc.file_name,
            'summary': {
                'total_cost': estimate.total_cost_inr,
                'total_cost_formatted': estimate.total_cost_formatted,
                'timeline_weeks': estimate.timeline_weeks,
                'team_size': team.total_team_size,
                'features_count': len(features.features),
                'complexity': features.complexity,
                'risk_level': estimate.risk_level
            },
            'features': [f['description'] for f in features.features],
            'modules': features.modules,
            'integrations': features.integrations,
            'cost_breakdown': {
                'feature_cost': estimate.cost.feature_cost,
                'platform_cost': estimate.cost.platform_cost,
                'ui_cost': estimate.cost.ui_cost,
                'integration_cost': estimate.cost.integration_cost,
                'testing_cost': estimate.cost.testing_cost,
                'pm_cost': estimate.cost.project_management_cost,
                'buffer_cost': estimate.cost.buffer_cost
            },
            'timeline': {
                'start_date': estimate.timeline.estimated_start,
                'end_date': estimate.timeline.estimated_end,
                'phases': estimate.timeline.phases
            },
            'team': [
                {'role': m.role, 'count': m.count, 'cost': m.total_cost}
                for m in team.team_members
            ]
        }
        
        json_str = json.dumps(report_data, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"srs_analysis_{project_id}.json",
            mime="application/json"
        )
    
    with col2:
        # CSV export (simplified)
        csv_data = f"""Parameter,Value
Project ID,{project_id}
Total Cost,{estimate.total_cost_formatted}
Timeline,{estimate.timeline_weeks} weeks
Team Size,{team.total_team_size}
Features,{len(features.features)}
Complexity,{features.complexity}
Risk Level,{estimate.risk_level}
Start Date,{estimate.timeline.estimated_start}
End Date,{estimate.timeline.estimated_end}
"""
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"srs_analysis_{project_id}.csv",
            mime="text/csv"
        )
    
    with col3:
        st.info("📧 Email report functionality coming soon!")


def show_sample_analysis():
    """Show analysis with sample data"""
    
    st.info("📊 Showing sample analysis with demo data...")
    
    # Create sample parsed document
    sample_doc = ParsedDocument(
        raw_text="""
        Sample E-Commerce Platform SRS
        
        The system shall allow users to browse products.
        The system shall implement a shopping cart functionality.
        Users should be able to make payments via multiple gateways.
        The application shall support push notifications.
        The system shall have an admin dashboard for management.
        Integration with SMS gateway for OTP verification.
        Real-time chat support for customers.
        The platform shall be available on web and mobile.
        """,
        file_name="sample_srs.pdf",
        word_count=100,
        page_count=5,
        parse_success=True
    )
    