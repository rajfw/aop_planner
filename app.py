import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import time

# ======================
# PAGE CONFIGURATION
# ======================
st.set_page_config(
    page_title="AOP Planner Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# CUSTOM CSS
# ======================
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3B82F6;
    }
    
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #3B82F6;
    }
    
    .feature-card {
        background: #F8FAFC;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    }
    
    .feature-list-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .status-pending { border-left: 4px solid #F59E0B; }
    .status-approved { border-left: 4px solid #10B981; }
    .status-rejected { border-left: 4px solid #EF4444; }
    .status-draft { border-left: 4px solid #6B7280; }
    
    .action-button {
        margin: 2px;
        padding: 4px 8px;
        font-size: 0.85rem;
    }
    
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .badge-ai { background-color: #DBEAFE; color: #1E40AF; }
    .badge-cx { background-color: #FCE7F3; color: #9D174D; }
    .badge-ex { background-color: #D1FAE5; color: #065F46; }
    .badge-ce { background-color: #FEF3C7; color: #92400E; }
    .badge-platform { background-color: #E0E7FF; color: #3730A3; }
    
    .dependency-item {
        background: #F3F4F6;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        border-left: 3px solid #3B82F6;
    }
    
    .dependency-team {
        font-weight: 600;
        color: #1E40AF;
        margin-bottom: 4px;
    }
    
    .dependency-title {
        font-weight: 500;
        color: #111827;
        margin: 4px 0;
    }
    
    .dependency-desc {
        color: #6B7280;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .dependency-container {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    .remove-btn {
        background-color: #FEE2E2;
        color: #DC2626;
        border: 1px solid #FCA5A5;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.8rem;
        cursor: pointer;
        margin-top: 5px;
    }
    
    .remove-btn:hover {
        background-color: #FECACA;
    }
</style>
""", unsafe_allow_html=True)

# ======================
# CONSTANTS
# ======================
BUSINESS_UNITS = ["AI BU", "CX BU", "EX BU", "CE BU", "Platform BU"]
PM_HEADS = ["AI BU PM Head", "CX BU PM Head", "EX BU PM Head", "CE BU PM Head", "Platform BU PM Head"]
CURRENT_YEAR = datetime.now().year

# ======================
# SESSION STATE INIT
# ======================
if 'features' not in st.session_state:
    st.session_state.features = []
if 'votes' not in st.session_state:
    st.session_state.votes = {}
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'edit_feature_id' not in st.session_state:
    st.session_state.edit_feature_id = None
if 'view_feature_id' not in st.session_state:
    st.session_state.view_feature_id = None
if 'dependency_count' not in st.session_state:
    st.session_state.dependency_count = 1

# ======================
# HELPER FUNCTIONS
# ======================
def get_bu_badge(bu):
    bu_lower = bu.lower()
    if "ai" in bu_lower:
        return "badge-ai"
    elif "cx" in bu_lower:
        return "badge-cx"
    elif "ex" in bu_lower:
        return "badge-ex"
    elif "ce" in bu_lower:
        return "badge-ce"
    elif "platform" in bu_lower:
        return "badge-platform"
    return ""

def get_status_badge(status):
    status_map = {
        "Draft": "🔵",
        "Submitted": "🟡",
        "Under Review": "🟠",
        "Approved": "🟢",
        "Rejected": "🔴"
    }
    return status_map.get(status, "⚪")

def save_feature(feature):
    """Save or update a feature"""
    if 'id' in feature and feature['id']:
        # Update existing feature
        for i, f in enumerate(st.session_state.features):
            if f['id'] == feature['id']:
                st.session_state.features[i] = feature
                return
    else:
        # Add new feature
        feature['id'] = f"F-{len(st.session_state.features)+1:04d}"
        feature['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.features.append(feature)

def delete_feature(feature_id):
    """Delete a feature by ID"""
    st.session_state.features = [f for f in st.session_state.features if f['id'] != feature_id]
    if feature_id in st.session_state.votes:
        del st.session_state.votes[feature_id]

def get_dependencies_by_team(dependency_details):
    """Organize dependencies by team"""
    team_deps = {}
    for dep in dependency_details:
        team = dep.get('team', '')
        if team:
            if team not in team_deps:
                team_deps[team] = []
            team_deps[team].append({
                'title': dep.get('title', ''),
                'description': dep.get('description', '')
            })
    return team_deps

def render_dependencies_html(dependency_details):
    """Render dependencies as HTML"""
    if not dependency_details:
        return "<p style='color: #6B7280; font-style: italic;'>No dependencies specified</p>"
    
    team_deps = get_dependencies_by_team(dependency_details)
    
    html = ""
    for team, deps in team_deps.items():
        badge_class = get_bu_badge(team)
        html += f"""
        <div class="dependency-item">
            <div class="dependency-team">
                <span class="{badge_class} badge">{team}</span>
            </div>
        """
        for dep in deps:
            if dep.get('title') or dep.get('description'):
                html += f"""
                <div style="margin: 8px 0 8px 10px; padding-left: 10px; border-left: 2px solid #D1D5DB;">
                    <div class="dependency-title">{dep.get('title', 'Untitled Dependency')}</div>
                    <div class="dependency-desc">{dep.get('description', 'No description provided')}</div>
                </div>
                """
        html += "</div>"
    
    return html

def reset_dependency_count():
    """Reset dependency count for new feature"""
    st.session_state.dependency_count = 1

# ======================
# SIDEBAR NAVIGATION
# ======================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092655.png", width=100)
    st.title("📋 AOP Planner")
    
    # Navigation
    st.subheader("Navigation")
    nav_options = ["🏠 Home", "📝 Submit New", "📋 List Features", "🔍 Analyze & Score", "🤝 Collaborate & Vote"]
    
    for option in nav_options:
        if option == "🏠 Home":
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                st.session_state.step = "home"
                st.rerun()
        elif option == "📝 Submit New":
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                reset_dependency_count()
                st.session_state.step = 1
                st.rerun()
        elif option == "📋 List Features":
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                st.session_state.step = "list"
                st.rerun()
        elif option == "🔍 Analyze & Score":
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                st.session_state.step = 2
                st.rerun()
        elif option == "🤝 Collaborate & Vote":
            if st.button(option, use_container_width=True, key=f"nav_{option}"):
                st.session_state.step = 3
                st.rerun()
    
    st.divider()
    
    # Quick Stats
    st.subheader("📊 Quick Stats")
    if st.session_state.features:
        total = len(st.session_state.features)
        by_status = {}
        by_bu = {}
        for f in st.session_state.features:
            by_status[f.get('status', 'Draft')] = by_status.get(f.get('status', 'Draft'), 0) + 1
            by_bu[f.get('bu', 'Unknown')] = by_bu.get(f.get('bu', 'Unknown'), 0) + 1
        
        st.metric("Total Features", total)
        
        with st.expander("By Status"):
            for status, count in by_status.items():
                st.write(f"{get_status_badge(status)} {status}: {count}")
        
        with st.expander("By BU"):
            for bu, count in by_bu.items():
                st.write(f"<span class='{get_bu_badge(bu)} badge'>{bu}</span>: {count}", unsafe_allow_html=True)
    
    st.divider()
    
    # Demo Data
    if st.button("🚀 Load Demo Data", use_container_width=True):
        demo_features = [
            {
                "id": "F-0001",
                "title": "AI-Powered Customer Segmentation",
                "description": "Advanced ML model for real-time customer segmentation using behavioral data",
                "bu": "AI BU",
                "year": 2025,
                "half": "H1",
                "quarter": "Q1",
                "type": "Hero Big Rock",
                "impact": 9,
                "effort": "L",
                "rice_score": 285.6,
                "competitor_score": 8,
                "dependency_details": [
                    {
                        "team": "CX BU",
                        "title": "Real-time Customer Data Feed",
                        "description": "Need access to real-time customer interaction data from CX systems"
                    },
                    {
                        "team": "CX BU",
                        "title": "Customer Feedback Integration",
                        "description": "Integration with CX feedback system for model training"
                    },
                    {
                        "team": "Platform BU",
                        "title": "ML Model Serving Infrastructure",
                        "description": "Requires GPU-enabled infrastructure for model serving and inference"
                    },
                    {
                        "team": "Platform BU",
                        "title": "Data Pipeline Setup",
                        "description": "Need data pipeline to process customer data in real-time"
                    }
                ],
                "prd_file": "prd_ai_segmentation.pdf",
                "mockup_file": "mockup_segmentation_dashboard.png",
                "submitted_by": "AI Team",
                "created_date": "2024-01-15 10:30:00",
                "status": "Under Review"
            },
            {
                "id": "F-0002",
                "title": "Unified Customer Dashboard",
                "description": "Single pane of glass for customer success metrics across all touchpoints",
                "bu": "CX BU",
                "year": 2025,
                "half": "H1",
                "quarter": "Q2",
                "type": "Big Rock",
                "impact": 8,
                "effort": "XL",
                "rice_score": 192.3,
                "competitor_score": 7,
                "dependency_details": [
                    {
                        "team": "Platform BU",
                        "title": "API Gateway Integration",
                        "description": "Need Platform BU to expose unified APIs from different backend systems"
                    },
                    {
                        "team": "Platform BU",
                        "title": "Authentication Service",
                        "description": "Integration with company-wide authentication service"
                    },
                    {
                        "team": "EX BU",
                        "title": "Employee Performance Data",
                        "description": "Access to EX employee performance metrics for customer success correlation"
                    },
                    {
                        "team": "EX BU",
                        "title": "Support Team Metrics",
                        "description": "Real-time metrics from support team performance"
                    },
                    {
                        "team": "AI BU",
                        "title": "Predictive Analytics",
                        "description": "AI models for predicting customer churn and satisfaction"
                    }
                ],
                "prd_file": "prd_customer_dashboard.pdf",
                "mockup_file": "mockup_dashboard_v1.fig",
                "submitted_by": "CX Team",
                "created_date": "2024-01-16 14:20:00",
                "status": "Submitted"
            },
            {
                "id": "F-0003",
                "title": "Employee Engagement Portal",
                "description": "Central portal for employee feedback, recognition, and engagement tracking",
                "bu": "EX BU",
                "year": 2025,
                "half": "H2",
                "quarter": "Q3",
                "type": "Hero Big Rock",
                "impact": 7,
                "effort": "L",
                "rice_score": 178.5,
                "competitor_score": 6,
                "dependency_details": [
                    {
                        "team": "Platform BU",
                        "title": "Authentication & Authorization",
                        "description": "Integrate with company SSO and implement role-based access control"
                    },
                    {
                        "team": "Platform BU",
                        "title": "Database Setup",
                        "description": "Need dedicated database for employee engagement data"
                    },
                    {
                        "team": "CE BU",
                        "title": "Customer Feedback Integration",
                        "description": "Link employee engagement scores with customer satisfaction metrics"
                    },
                    {
                        "team": "CE BU",
                        "title": "NPS Data Sync",
                        "description": "Sync Net Promoter Score data with employee performance"
                    },
                    {
                        "team": "AI BU",
                        "title": "Sentiment Analysis",
                        "description": "AI-powered sentiment analysis on employee feedback"
                    }
                ],
                "prd_file": "prd_employee_portal.pdf",
                "mockup_file": None,
                "submitted_by": "EX Team",
                "created_date": "2024-01-17 09:15:00",
                "status": "Draft"
            }
        ]
        st.session_state.features = demo_features
        st.success("Demo data loaded!")
        st.rerun()
    
    if st.button("🔄 Reset All", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.step = "home"
        st.session_state.dependency_count = 1
        st.rerun()

# ======================
# HOME PAGE
# ======================
def home_page():
    st.markdown('<h1 class="main-header">🏠 AOP Planner Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.features:
        st.info("No features added yet. Start by submitting a new feature request.")
        if st.button("📝 Submit First Feature", type="primary"):
            reset_dependency_count()
            st.session_state.step = 1
            st.rerun()
        return
    
    # Summary Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(st.session_state.features)
        st.metric("Total Features", total)
    
    with col2:
        pending = len([f for f in st.session_state.features if f.get('status') in ['Draft', 'Submitted', 'Under Review']])
        st.metric("Pending Review", pending)
    
    with col3:
        approved = len([f for f in st.session_state.features if f.get('status') == 'Approved'])
        st.metric("Approved", approved)
    
    with col4:
        hero_rocks = len([f for f in st.session_state.features if 'Hero' in f.get('type', '')])
        st.metric("Hero Big Rocks", hero_rocks)
    
    st.divider()
    
    # Recent Features
    st.subheader("📋 Recent Feature Requests")
    
    # Sort by creation date (newest first)
    sorted_features = sorted(st.session_state.features, 
                           key=lambda x: x.get('created_date', ''), 
                           reverse=True)
    
    for feature in sorted_features[:8]:  # Show only 8 most recent
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                badge_class = get_bu_badge(feature['bu'])
                status_badge = get_status_badge(feature.get('status', 'Draft'))
                
                # Get dependent teams from dependency details
                dependent_teams = list(set([dep.get('team', '') for dep in feature.get('dependency_details', []) if dep.get('team')]))
                
                # Count total dependencies
                total_deps = len(feature.get('dependency_details', []))
                
                st.markdown(f"""
                <div class="feature-list-card status-{feature.get('status', 'Draft').lower().replace(' ', '-')}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0;">{feature['title']}</h4>
                        <span style="font-size: 0.9rem; color: #6B7280;">{feature['id']}</span>
                    </div>
                    <p style="margin: 8px 0; color: #4B5563;">{feature['description'][:150]}...</p>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
                        <span class="{badge_class} badge">{feature['bu']}</span>
                        <span style="background-color: #E5E7EB; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                            {feature['year']} {feature['half']}-{feature['quarter']}
                        </span>
                        <span style="background-color: #F3F4F6; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                            {feature['type']}
                        </span>
                        <span style="background-color: #FEF3C7; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                            Impact: {feature.get('impact', 'N/A')}/10
                        </span>
                        <span style="background-color: #D1FAE5; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                            {status_badge} {feature.get('status', 'Draft')}
                        </span>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.85rem;">
                        <strong>Dependent Teams:</strong> {', '.join(dependent_teams) if dependent_teams else 'None'}
                        <span style="margin-left: 10px; color: #6B7280;">
                            ({total_deps} dependency{'' if total_deps == 1 else 's'})
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Action buttons
                if st.button("👁️ View", key=f"home_view_{feature['id']}", use_container_width=True):
                    st.session_state.view_feature_id = feature['id']
                    st.session_state.step = "view"
                    st.rerun()
                
                if st.button("✏️ Edit", key=f"home_edit_{feature['id']}", use_container_width=True):
                    reset_dependency_count()
                    st.session_state.edit_feature_id = feature['id']
                    st.session_state.step = 1
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"home_delete_{feature['id']}", use_container_width=True):
                    delete_feature(feature['id'])
                    st.success(f"Feature {feature['id']} deleted!")
                    time.sleep(0.5)
                    st.rerun()
    
    # Show all features button if there are more
    if len(st.session_state.features) > 8:
        if st.button("📋 View All Features", use_container_width=True):
            st.session_state.step = "list"
            st.rerun()
    
    st.divider()
    
    # Visualization
    if st.session_state.features:
        st.subheader("📈 Feature Distribution")
        
        tab1, tab2 = st.tabs(["By Business Unit", "By Status"])
        
        with tab1:
            bu_counts = {}
            for f in st.session_state.features:
                bu_counts[f['bu']] = bu_counts.get(f['bu'], 0) + 1
            
            if bu_counts:
                fig = px.pie(values=list(bu_counts.values()), 
                           names=list(bu_counts.keys()),
                           title="Features by Business Unit")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            status_counts = {}
            for f in st.session_state.features:
                status_counts[f.get('status', 'Draft')] = status_counts.get(f.get('status', 'Draft'), 0) + 1
            
            if status_counts:
                fig = px.bar(x=list(status_counts.keys()), 
                           y=list(status_counts.values()),
                           title="Features by Status",
                           labels={'x': 'Status', 'y': 'Count'})
                st.plotly_chart(fig, use_container_width=True)

# ======================
# STEP 1: SUBMIT/EDIT FEATURE
# ======================
def step1_submit():
    # Determine if editing or creating
    is_editing = st.session_state.edit_feature_id is not None
    
    if is_editing:
        # Find the feature being edited
        feature_to_edit = None
        for f in st.session_state.features:
            if f['id'] == st.session_state.edit_feature_id:
                feature_to_edit = f
                break
        
        if not feature_to_edit:
            st.error("Feature not found!")
            st.session_state.edit_feature_id = None
            st.rerun()
        
        title = f"✏️ Edit Feature: {feature_to_edit['title']}"
        submit_button_text = "💾 Update Feature"
        
        # Get existing dependency details
        existing_deps = feature_to_edit.get('dependency_details', [])
        if existing_deps:
            st.session_state.dependency_count = len(existing_deps)
    else:
        title = "📝 Submit New Feature Request"
        submit_button_text = "🚀 Submit Feature Request"
        existing_deps = []
    
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Basic Information
            st.subheader("Basic Information")
            
            feature_title = st.text_input(
                "Feature Title*", 
                value=feature_to_edit['title'] if is_editing else "",
                placeholder="AI-powered analytics dashboard"
            )
            
            description = st.text_area(
                "Description*", 
                value=feature_to_edit['description'] if is_editing else "",
                height=100,
                placeholder="Describe the feature, business value, and user impact..."
            )
            
            bu = st.selectbox(
                "Owning Business Unit*", 
                BUSINESS_UNITS,
                index=BUSINESS_UNITS.index(feature_to_edit['bu']) if is_editing else 0
            )
            
            # Target Year (greater than current year)
            future_years = [CURRENT_YEAR + i for i in range(1, 6)]  # Next 5 years
            year = st.selectbox(
                "Target Year*", 
                future_years,
                index=future_years.index(feature_to_edit['year']) if is_editing and feature_to_edit['year'] in future_years else 0
            )
            
        with col2:
            # Planning Details
            st.subheader("Planning Details")
            
            half = st.radio("Half-Year*", ["H1", "H2"], 
                          horizontal=True,
                          index=0 if not is_editing or feature_to_edit['half'] == "H1" else 1)
            
            # Quarters based on half-year
            if half == "H1":
                quarters = ["Q1", "Q2"]
            else:
                quarters = ["Q3", "Q4"]
            
            quarter = st.selectbox(
                "Quarter*",
                quarters,
                index=quarters.index(feature_to_edit['quarter']) if is_editing and feature_to_edit['quarter'] in quarters else 0
            )
            
            rock_types = {
                "H1": ["Hero Big Rock", "Big Rock", "Small Rock"],
                "H2": ["Hero Big Rock", "Big Rock", "Small Rock"]
            }
            rock_type = st.selectbox(
                "Feature Type*", 
                rock_types[half],
                index=rock_types[half].index(feature_to_edit['type']) if is_editing and feature_to_edit['type'] in rock_types[half] else 0
            )
            
            business_impact = st.slider(
                "Business Impact (1-10)*", 
                1, 10, 
                value=feature_to_edit.get('impact', 7) if is_editing else 7
            )
            
            effort = st.select_slider(
                "Effort Estimate*", 
                ["XS", "S", "M", "L", "XL"],
                value=feature_to_edit.get('effort', 'M') if is_editing else "M"
            )
        
        # Dependencies & Attachments
        st.subheader("Dependent Functionality/Needs")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Map Dependencies to Teams (One-to-Many)**")
            st.caption("You can add multiple dependencies for the same or different teams.")
            
            # Initialize dependency details from session state or existing data
            if is_editing and existing_deps:
                dependency_details = existing_deps.copy()
                # Ensure we have at least the right number of dependencies
                if len(dependency_details) < st.session_state.dependency_count:
                    # Add empty dependencies if needed
                    for i in range(len(dependency_details), st.session_state.dependency_count):
                        dependency_details.append({"team": "", "title": "", "description": ""})
            else:
                dependency_details = []
                # Initialize with current count
                for i in range(st.session_state.dependency_count):
                    if i < len(existing_deps):
                        dependency_details.append(existing_deps[i])
                    else:
                        dependency_details.append({"team": "", "title": "", "description": ""})
            
            # Display dependency input fields
            new_dependency_details = []
            
            for i in range(st.session_state.dependency_count):
                with st.container():
                    st.markdown(f"<div class='dependency-container'>", unsafe_allow_html=True)
                    st.markdown(f"**Dependency {i+1}**")
                    
                    # Get current dependency data
                    current_dep = dependency_details[i] if i < len(dependency_details) else {"team": "", "title": "", "description": ""}
                    
                    # Team selection for this dependency
                    dep_team = st.selectbox(
                        f"Select Dependent Team {i+1}",
                        [""] + BUSINESS_UNITS,
                        index=0 if not current_dep.get('team') else BUSINESS_UNITS.index(current_dep['team']) + 1,
                        key=f"dep_team_{i}"
                    )
                    
                    # Dependency title and description
                    dep_title = st.text_input(
                        f"Dependency Title {i+1}",
                        value=current_dep.get('title', ''),
                        placeholder="e.g., API Integration, Data Feed, Infrastructure",
                        key=f"dep_title_{i}"
                    )
                    
                    dep_desc = st.text_area(
                        f"Dependency Description {i+1}",
                        value=current_dep.get('description', ''),
                        placeholder="Specific functionality, support, or resource needed from this team",
                        height=60,
                        key=f"dep_desc_{i}"
                    )
                    
                    # Remove button for this dependency (not for the first one)
                    if i > 0:
                        col_remove, _ = st.columns([1, 5])
                        with col_remove:
                            if st.button(f"❌ Remove", key=f"remove_{i}", use_container_width=True):
                                # Remove this dependency by decreasing count
                                st.session_state.dependency_count -= 1
                                st.rerun()
                    
                    st.markdown(f"</div>", unsafe_allow_html=True)
                    
                    # Only add if team is selected
                    if dep_team:
                        new_dependency_details.append({
                            "team": dep_team,
                            "title": dep_title,
                            "description": dep_desc
                        })
                    elif dep_title or dep_desc:
                        # If user entered title/description but no team, warn them
                        st.warning(f"Please select a team for dependency {i+1} or clear the fields.")
            
            # Add more dependency button
            col_add, _ = st.columns([2, 5])
            with col_add:
                if st.button("➕ Add Another Dependency", key="add_dep", use_container_width=True):
                    st.session_state.dependency_count += 1
                    st.rerun()
            
            # Show summary of selected dependencies
            if new_dependency_details:
                st.write("**Selected Dependencies Summary:**")
                
                # Group by team
                team_groups = {}
                for dep in new_dependency_details:
                    team = dep['team']
                    if team not in team_groups:
                        team_groups[team] = []
                    team_groups[team].append(dep)
                
                for team, deps in team_groups.items():
                    badge_class = get_bu_badge(team)
                    st.markdown(f"<span class='{badge_class} badge'>{team}</span>: {len(deps)} dependency{'s' if len(deps) > 1 else ''}", unsafe_allow_html=True)
                    for dep in deps:
                        if dep.get('title'):
                            st.markdown(f"  • {dep['title']}")
        
        with col4:
            st.subheader("Attachments")
            
            # Separate PRD and Mockup uploads
            prd_file = st.file_uploader(
                "Upload PRD (Product Requirements Document)*",
                type=['pdf', 'docx', 'txt'],
                key="prd_uploader"
            )
            
            mockup_file = st.file_uploader(
                "Upload Mockups (Optional)",
                type=['png', 'jpg', 'jpeg', 'fig', 'xd'],
                key="mockup_uploader"
            )
            
            if is_editing:
                if feature_to_edit.get('prd_file'):
                    st.info(f"📄 Current PRD: {feature_to_edit['prd_file']}")
                if feature_to_edit.get('mockup_file'):
                    st.info(f"🎨 Current Mockup: {feature_to_edit['mockup_file']}")
        
        # Status selection (only for editing)
        if is_editing:
            status = st.selectbox(
                "Status",
                ["Draft", "Submitted", "Under Review", "Approved", "Rejected"],
                index=["Draft", "Submitted", "Under Review", "Approved", "Rejected"].index(
                    feature_to_edit.get('status', 'Draft')
                )
            )
        else:
            status = "Draft"
        
        # Submit/Update button
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            if st.button(submit_button_text, type="primary", use_container_width=True):
                if feature_title and description:
                    # Extract dependent teams from dependency details
                    dependent_teams = list(set([dep['team'] for dep in new_dependency_details if dep.get('team')]))
                    
                    feature_data = {
                        "id": feature_to_edit['id'] if is_editing else None,
                        "title": feature_title,
                        "description": description,
                        "bu": bu,
                        "year": year,
                        "half": half,
                        "quarter": quarter,
                        "type": rock_type,
                        "impact": business_impact,
                        "effort": effort,
                        "dependency_details": new_dependency_details,
                        "dependent_teams": dependent_teams,  # Derived from dependency details
                        "prd_file": prd_file.name if prd_file else feature_to_edit.get('prd_file') if is_editing else None,
                        "mockup_file": mockup_file.name if mockup_file else feature_to_edit.get('mockup_file') if is_editing else None,
                        "submitted_by": feature_to_edit.get('submitted_by', 'User') if is_editing else "Current User",
                        "status": status,
                        "rice_score": feature_to_edit.get('rice_score', 0) if is_editing else 0,
                        "competitor_score": feature_to_edit.get('competitor_score', 0) if is_editing else 0,
                        "created_date": feature_to_edit.get('created_date') if is_editing else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    save_feature(feature_data)
                    
                    if is_editing:
                        st.success(f"✅ Feature {feature_to_edit['id']} updated successfully!")
                    else:
                        st.success("✅ Feature request submitted successfully!")
                    
                    # Clear edit state and reset dependency count
                    st.session_state.edit_feature_id = None
                    reset_dependency_count()
                    
                    time.sleep(1)
                    st.session_state.step = "home"
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields (Title and Description)")
        
        with col_btn2:
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.edit_feature_id = None
                reset_dependency_count()
                st.session_state.step = "home"
                st.rerun()
        
        with col_btn3:
            if st.button("📋 View All Features", use_container_width=True):
                st.session_state.edit_feature_id = None
                reset_dependency_count()
                st.session_state.step = "list"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# LIST FEATURES PAGE
# ======================
def list_features_page():
    st.markdown('<h1 class="main-header">📋 All Feature Requests</h1>', unsafe_allow_html=True)
    
    if not st.session_state.features:
        st.info("No features found. Submit your first feature request!")
        if st.button("📝 Submit First Feature", type="primary"):
            reset_dependency_count()
            st.session_state.step = 1
            st.rerun()
        return
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_bu = st.selectbox("Filter by BU", ["All"] + BUSINESS_UNITS)
    
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All", "Draft", "Submitted", "Under Review", "Approved", "Rejected"])
    
    with col3:
        filter_year = st.selectbox("Filter by Year", ["All"] + list(sorted(set([f['year'] for f in st.session_state.features]))))
    
    with col4:
        filter_type = st.selectbox("Filter by Type", ["All", "Hero Big Rock", "Big Rock", "Small Rock"])
    
    # Apply filters
    filtered_features = st.session_state.features.copy()
    
    if filter_bu != "All":
        filtered_features = [f for f in filtered_features if f['bu'] == filter_bu]
    
    if filter_status != "All":
        filtered_features = [f for f in filtered_features if f.get('status') == filter_status]
    
    if filter_year != "All":
        filtered_features = [f for f in filtered_features if f['year'] == filter_year]
    
    if filter_type != "All":
        filtered_features = [f for f in filtered_features if f['type'] == filter_type]
    
    # Display features
    st.write(f"**Showing {len(filtered_features)} of {len(st.session_state.features)} features**")
    
    for feature in filtered_features:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                badge_class = get_bu_badge(feature['bu'])
                status_badge = get_status_badge(feature.get('status', 'Draft'))
                
                # Get dependent teams from dependency details
                dependent_teams = list(set([dep.get('team', '') for dep in feature.get('dependency_details', []) if dep.get('team')]))
                
                # Count total dependencies
                total_deps = len(feature.get('dependency_details', []))
                
                # Render dependencies HTML
                deps_html = render_dependencies_html(feature.get('dependency_details', []))
                
                st.markdown(f"""
                <div class="feature-list-card status-{feature.get('status', 'Draft').lower().replace(' ', '-')}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0 0 8px 0;">{feature['title']}</h4>
                            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
                                <span class="{badge_class} badge">{feature['bu']}</span>
                                <span style="background-color: #E5E7EB; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                                    {feature['year']} {feature['half']}-{feature['quarter']}
                                </span>
                                <span style="background-color: #F3F4F6; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                                    {feature['type']}
                                </span>
                                <span style="background-color: #FEF3C7; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                                    Impact: {feature.get('impact', 'N/A')}/10
                                </span>
                                <span style="background-color: #D1FAE5; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">
                                    {status_badge} {feature.get('status', 'Draft')}
                                </span>
                            </div>
                        </div>
                        <span style="font-size: 0.9rem; color: #6B7280;">{feature['id']}</span>
                    </div>
                    <p style="margin: 8px 0; color: #4B5563;">{feature['description'][:200]}...</p>
                    <div style="margin-top: 10px;">
                        <p style="margin: 5px 0; font-size: 0.9rem;">
                            <strong>Dependent Teams:</strong> {', '.join(dependent_teams) if dependent_teams else 'None'}
                            <span style="margin-left: 10px; color: #6B7280;">
                                ({total_deps} dependency{'' if total_deps == 1 else 's'})
                            </span>
                        </p>
                        <div style="margin: 10px 0;">
                            <strong>Dependent Functionality/Needs:</strong>
                            {deps_html}
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.8rem; color: #6B7280;">
                        Created: {feature.get('created_date', 'Unknown')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Action buttons
                if st.button("👁️ View", key=f"list_view_{feature['id']}", use_container_width=True):
                    st.session_state.view_feature_id = feature['id']
                    st.session_state.step = "view"
                    st.rerun()
                
                if st.button("✏️ Edit", key=f"list_edit_{feature['id']}", use_container_width=True):
                    reset_dependency_count()
                    st.session_state.edit_feature_id = feature['id']
                    st.session_state.step = 1
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"list_delete_{feature['id']}", use_container_width=True):
                    delete_feature(feature['id'])
                    st.success(f"Feature {feature['id']} deleted!")
                    time.sleep(0.5)
                    st.rerun()
    
    # Back button
    if st.button("← Back to Home", use_container_width=True):
        st.session_state.step = "home"
        st.rerun()

# ======================
# VIEW FEATURE PAGE
# ======================
def view_feature_page():
    if st.session_state.view_feature_id is None:
        st.error("No feature selected to view!")
        st.session_state.step = "home"
        st.rerun()
    
    # Find the feature
    feature_to_view = None
    for f in st.session_state.features:
        if f['id'] == st.session_state.view_feature_id:
            feature_to_view = f
            break
    
    if not feature_to_view:
        st.error("Feature not found!")
        st.session_state.view_feature_id = None
        st.session_state.step = "home"
        st.rerun()
    
    st.markdown(f'<h1 class="main-header">👁️ View Feature: {feature_to_view["title"]}</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        
        # Header with ID and Status
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                <span style="font-size: 1.2rem; font-weight: bold; color: #1E3A8A;">{feature_to_view['id']}</span>
                <span style="background-color: {'#10B981' if feature_to_view.get('status') == 'Approved' else '#F59E0B' if feature_to_view.get('status') == 'Under Review' else '#6B7280'}; 
                      color: white; padding: 4px 12px; border-radius: 20px; font-weight: 500;">
                    {feature_to_view.get('status', 'Draft')}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✏️ Edit this Feature", use_container_width=True):
                reset_dependency_count()
                st.session_state.edit_feature_id = feature_to_view['id']
                st.session_state.view_feature_id = None
                st.session_state.step = 1
                st.rerun()
        
        # Feature Details in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Basic Information")
            st.markdown(f"**Title:** {feature_to_view['title']}")
            st.markdown(f"**Description:**  \n{feature_to_view['description']}")
            st.markdown(f"**Owning BU:** <span class='{get_bu_badge(feature_to_view['bu'])} badge'>{feature_to_view['bu']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Submitted by:** {feature_to_view.get('submitted_by', 'Unknown')}")
            st.markdown(f"**Created:** {feature_to_view.get('created_date', 'Unknown')}")
        
        with col2:
            st.subheader("📅 Planning Details")
            st.markdown(f"**Target Year:** {feature_to_view['year']}")
            st.markdown(f"**Timeline:** {feature_to_view['half']}-{feature_to_view['quarter']}")
            st.markdown(f"**Feature Type:** {feature_to_view['type']}")
            st.markdown(f"**Business Impact:** {feature_to_view.get('impact', 'N/A')}/10")
            st.markdown(f"**Effort Estimate:** {feature_to_view.get('effort', 'N/A')}")
            
            if feature_to_view.get('rice_score', 0) > 0:
                st.markdown(f"**RICE Score:** {feature_to_view.get('rice_score', 'N/A')}")
            if feature_to_view.get('competitor_score', 0) > 0:
                st.markdown(f"**Competitor Score:** {feature_to_view.get('competitor_score', 'N/A')}/10")
        
        # Dependencies - Now properly mapped with one-to-many
        st.subheader("🔗 Dependent Functionality/Needs by Team")
        
        # Get dependent teams from dependency details
        dependent_teams = list(set([dep.get('team', '') for dep in feature_to_view.get('dependency_details', []) if dep.get('team')]))
        total_deps = len(feature_to_view.get('dependency_details', []))
        
        if dependent_teams:
            st.markdown(f"**Dependent Teams:** {', '.join(dependent_teams)} ({total_deps} dependency{'s' if total_deps > 1 else ''})")
            
            # Render dependencies organized by team
            deps_html = render_dependencies_html(feature_to_view.get('dependency_details', []))
            st.markdown(deps_html, unsafe_allow_html=True)
        else:
            st.info("No dependencies specified for this feature")
        
        # Attachments
        st.subheader("📎 Attachments")
        col1, col2 = st.columns(2)
        
        with col1:
            if feature_to_view.get('prd_file'):
                st.success(f"✅ PRD: {feature_to_view['prd_file']}")
            else:
                st.warning("⚠️ No PRD uploaded")
        
        with col2:
            if feature_to_view.get('mockup_file'):
                st.success(f"✅ Mockups: {feature_to_view['mockup_file']}")
            else:
                st.info("ℹ️ No mockups uploaded")
        
        # Navigation buttons
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.view_feature_id = None
                st.session_state.step = "home"
                st.rerun()
        
        with col2:
            if st.button("📋 View All Features", use_container_width=True):
                st.session_state.view_feature_id = None
                st.session_state.step = "list"
                st.rerun()
        
        with col3:
            if st.button("🗑️ Delete this Feature", use_container_width=True):
                delete_feature(feature_to_view['id'])
                st.session_state.view_feature_id = None
                st.success(f"Feature {feature_to_view['id']} deleted!")
                time.sleep(0.5)
                st.session_state.step = "home"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# STEP 2: ANALYZE & SCORE
# ======================
def step2_analyze():
    st.markdown('<h1 class="main-header">🔍 Analyze & Prioritize</h1>', unsafe_allow_html=True)
    
    if not st.session_state.features:
        st.warning("No features submitted yet. Go to Submit page to add features.")
        if st.button("← Go to Home", use_container_width=True):
            st.session_state.step = "home"
            st.rerun()
        return
    
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        
        # Show all submitted features
        st.subheader("📋 Features to Analyze")
        
        # Filter features that need analysis
        features_to_analyze = [f for f in st.session_state.features 
                             if f.get('status') in ['Submitted', 'Under Review', 'Draft']]
        
        if not features_to_analyze:
            st.info("All features have been analyzed. Add new features or update existing ones.")
        
        features_df = pd.DataFrame(st.session_state.features)
        
        # Display in a nice table with dependency info
        if not features_df.empty:
            # Create a column for dependent teams summary
            def get_dependent_teams_summary(deps):
                teams = list(set([dep.get('team', '') for dep in deps if dep.get('team')]))
                return ', '.join(teams) if teams else 'None'
            
            def get_dependency_count(deps):
                return len(deps)
            
            features_df['dependent_teams'] = features_df['dependency_details'].apply(get_dependent_teams_summary)
            features_df['dependency_count'] = features_df['dependency_details'].apply(get_dependency_count)
            
            display_cols = ["id", "title", "bu", "type", "impact", "effort", "status", "rice_score", "dependent_teams", "dependency_count"]
            st.dataframe(features_df[display_cols], use_container_width=True)
        
        # Competitor Analysis Section
        st.subheader("🎯 Competitor Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            competitor = st.selectbox("Select Competitor for Analysis",
                                    ["Competitor A", "Competitor B", "Competitor C", "All Competitors"])
        
        with col2:
            analysis_depth = st.select_slider("Analysis Depth",
                                           ["Basic", "Detailed", "Comprehensive"])
        
        if st.button("🔍 Run Competitor Analysis", use_container_width=True):
            with st.spinner("Analyzing competitors..."):
                time.sleep(2)
                # Mock competitor analysis
                for feature in st.session_state.features:
                    # Simple mock scoring based on keywords
                    keywords = ["AI", "analytics", "mobile", "redesign", "automation", "customer", "dashboard"]
                    score = sum(1 for kw in keywords if kw.lower() in feature['title'].lower() or kw.lower() in feature['description'].lower())
                    feature['competitor_score'] = min(score * 2, 10)
                st.success("✅ Competitor analysis completed!")
        
        # RICE Scoring Section
        st.subheader("📊 RICE Scoring")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            reach_weight = st.slider("Reach Weight", 0.0, 1.0, 0.4)
        
        with col2:
            impact_weight = st.slider("Impact Weight", 0.0, 1.0, 0.3)
        
        with col3:
            confidence_weight = st.slider("Confidence Weight", 0.0, 1.0, 0.2)
        
        with col4:
            effort_weight = st.slider("Effort Weight", 0.0, 1.0, 0.1)
        
        if st.button("🧮 Calculate RICE Scores", type="primary", use_container_width=True):
            with st.spinner("Calculating RICE scores..."):
                time.sleep(1)
                for feature in st.session_state.features:
                    # Mock RICE calculation
                    reach = feature.get('impact', 5) * 1000
                    impact = feature.get('impact', 5) / 2.5
                    confidence = 0.8
                    effort_map = {"XS": 1, "S": 2, "M": 3, "L": 5, "XL": 8}
                    effort = effort_map.get(feature.get('effort', 'M'), 3)
                    
                    rice_score = (reach * reach_weight + 
                                 impact * impact_weight * 100 + 
                                 confidence * confidence_weight * 100) / (effort * effort_weight)
                    
                    feature['rice_score'] = round(rice_score, 2)
                
                st.success("✅ RICE scoring completed!")
        
        # Show Results
        if any(f.get('rice_score', 0) > 0 for f in st.session_state.features):
            st.subheader("📈 Prioritization Results")
            
            # Create results dataframe
            results_df = pd.DataFrame(st.session_state.features)
            results_df = results_df.sort_values('rice_score', ascending=False)
            
            # Add dependent teams column
            results_df['dependent_teams'] = results_df['dependency_details'].apply(
                lambda deps: ', '.join(list(set([dep.get('team', '') for dep in deps if dep.get('team')]))) or 'None'
            )
            
            results_df['dependency_count'] = results_df['dependency_details'].apply(len)
            
            # Display with colors
            st.dataframe(
                results_df[['id', 'title', 'bu', 'rice_score', 'competitor_score', 'type', 'dependent_teams', 'dependency_count']].style.background_gradient(
                    subset=['rice_score'], cmap='RdYlGn'
                ),
                use_container_width=True
            )
            
            # Visualization
            fig = px.bar(results_df.head(10), 
                        x='title', y='rice_score',
                        color='bu',
                        title="Top 10 Features by RICE Score")
            st.plotly_chart(fig, use_container_width=True)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.step = "home"
                st.rerun()
        
        with col2:
            if st.button("Next → Collaborate & Vote", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# STEP 3: COLLABORATE & VOTE
# ======================
def step3_collaborate():
    st.markdown('<h1 class="main-header">🤝 Collaborate & Approve</h1>', unsafe_allow_html=True)
    
    if not st.session_state.features:
        st.warning("No features to review. Add features first.")
        if st.button("← Back to Home"):
            st.session_state.step = "home"
            st.rerun()
        return
    
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        
        # PM Head Selection
        st.subheader("👥 PM Head Dashboard")
        pm_name = st.selectbox("Select Your Role", PM_HEADS)
        
        st.info(f"Welcome, **{pm_name}!** You have voting rights for all features.")
        
        # Voting Interface
        st.subheader("🗳️ Feature Review Board")
        
        # Create tabs for different feature types
        tab1, tab2, tab3 = st.tabs(["Hero Big Rocks", "Big Rocks", "Small Rocks"])
        
        with tab1:
            hero_features = [f for f in st.session_state.features if 'Hero' in f.get('type', '')]
            display_voting_board(hero_features, pm_name)
        
        with tab2:
            big_features = [f for f in st.session_state.features if 'Big' in f.get('type', '') and 'Hero' not in f.get('type', '')]
            display_voting_board(big_features, pm_name)
        
        with tab3:
            small_features = [f for f in st.session_state.features if 'Small' in f.get('type', '')]
            display_voting_board(small_features, pm_name)
        
        # Real-time Results
        st.subheader("📊 Voting Results")
        
        if st.session_state.votes:
            votes_df = pd.DataFrame([
                {"feature": k, "approve": v.get('approve', 0), "reject": v.get('reject', 0)}
                for k, v in st.session_state.votes.items()
            ])
            
            if not votes_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(votes_df, use_container_width=True)
                
                with col2:
                    fig = px.pie(votes_df.melt(id_vars=['feature'], 
                                             value_vars=['approve', 'reject']),
                               values='value', names='variable',
                               title="Overall Voting Distribution")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.step = "home"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_voting_board(features, pm_name):
    if not features:
        st.info("No features in this category")
        return
    
    for feature in features:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                badge_class = get_bu_badge(feature['bu'])
                
                # Get dependent teams summary
                dependent_teams = list(set([dep.get('team', '') for dep in feature.get('dependency_details', []) if dep.get('team')]))
                deps_summary = ', '.join(dependent_teams) if dependent_teams else 'None'
                total_deps = len(feature.get('dependency_details', []))
                
                st.markdown(f"""
                <div class="feature-card status-{feature.get('status', 'Draft').lower().replace(' ', '-')}">
                    <h4>{feature['title']}</h4>
                    <p><strong>BU:</strong> <span class='{badge_class} badge'>{feature['bu']}</span> | 
                    <strong>Type:</strong> {feature['type']}</p>
                    <p><strong>RICE Score:</strong> {feature.get('rice_score', 'N/A')} | 
                    <strong>Competitor Pressure:</strong> {feature.get('competitor_score', 'N/A')}/10</p>
                    <p><strong>Timeline:</strong> {feature['year']} {feature['half']}-{feature['quarter']}</p>
                    <p><strong>Dependent Teams:</strong> {deps_summary} ({total_deps} dependency{'s' if total_deps > 1 else ''})</p>
                    <p><strong>Status:</strong> {get_status_badge(feature.get('status', 'Draft'))} {feature.get('status', 'Draft')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                vote_key = f"vote_{feature['id']}_{pm_name}"
                if st.button(f"✅ Approve", key=f"approve_{vote_key}", use_container_width=True):
                    vote_for_feature(feature['id'], pm_name, 'approve')
                    st.success(f"Voted APPROVE for {feature['title']}")
                    time.sleep(0.5)
                    st.rerun()
            
            with col3:
                if st.button(f"❌ Reject", key=f"reject_{vote_key}", use_container_width=True):
                    vote_for_feature(feature['id'], pm_name, 'reject')
                    st.error(f"Voted REJECT for {feature['title']}")
                    time.sleep(0.5)
                    st.rerun()
            
            # Show current votes
            current_votes = st.session_state.votes.get(feature['id'], {})
            approve_count = current_votes.get('approve', 0)
            reject_count = current_votes.get('reject', 0)
            
            st.caption(f"✅ {approve_count} approve | ❌ {reject_count} reject")

def vote_for_feature(feature_id, pm_name, vote_type):
    if feature_id not in st.session_state.votes:
        st.session_state.votes[feature_id] = {'approve': 0, 'reject': 0}
    
    st.session_state.votes[feature_id][vote_type] += 1
    
    # Update feature status based on votes
    for feature in st.session_state.features:
        if feature['id'] == feature_id:
            votes = st.session_state.votes[feature_id]
            total_votes = votes.get('approve', 0) + votes.get('reject', 0)
            
            if total_votes >= 3:  # Threshold for decision
                if votes.get('approve', 0) > votes.get('reject', 0):
                    feature['status'] = 'Approved'
                else:
                    feature['status'] = 'Rejected'
            elif total_votes > 0:
                feature['status'] = 'Under Review'
            break

# ======================
# MAIN APP ROUTING
# ======================
def main():
    # Determine current page based on step
    current_step = st.session_state.get('step', 'home')
    
    if current_step == "home":
        home_page()
    elif current_step == "list":
        list_features_page()
    elif current_step == "view":
        view_feature_page()
    elif current_step == 1:
        step1_submit()
    elif current_step == 2:
        step2_analyze()
    elif current_step == 3:
        step3_collaborate()
    else:
        home_page()
    
    # Footer
    st.divider()
    st.caption(f"AOP Planner Pro | {CURRENT_YEAR} Hackathon Edition | Built with Streamlit")

if __name__ == "__main__":
    main()