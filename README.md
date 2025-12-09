📋 AOP Planner Pro
🎯 Project Summary
AOP Planner Pro is an Annual Operating Plan (AOP) Planning Tool that centralizes feature intake from multiple Business Units (BUs), automates prioritization using the RICE framework, and enables collaborative validation by PM leadership.

🏗️ Application Architecture

Framework: Streamlit (Python-based, no HTML/CSS required)
Data Storage: Session State (in-memory)
Visualization: Plotly for charts, Pandas for data manipulation
Styling: Custom CSS within Streamlit components


✅ Key Features

Multi-step workflow for AOP planning
BU-specific feature submission
One-to-many dependency mapping
RICE scoring & competitor analysis
Collaborative PM voting system
Full CRUD operations (Create, Read, Update, Delete)


📱 Page-by-Page Breakdown
🏠 Home Dashboard

Sidebar navigation
Quick stats (Total Features, Pending Review, Approved, Hero Big Rocks)
Recent features list
Visualization charts (Features by BU, Features by Status)

📝 Submit/Edit Feature

Form sections:

Basic Info (Title, Description, BU, Year)
Planning Details (Half-Year, Quarter, Feature Type, Impact, Effort)
Dependencies (One-to-many mapping)
Attachments (PRD, Mockups)


Status workflow: Draft → Submitted → Under Review → Approved/Rejected

📋 List Features

Filters by BU, Status, Year, Type
Feature cards with badges, timeline, impact score, dependencies
Actions: View, Edit, Delete

🔍 Analyze & Score

Competitor analysis (mock implementation)
RICE scoring with adjustable weights
Prioritized feature table + Top 10 visualization

🤝 Collaborate & Vote

PM heads review features by category (Hero Big Rocks, Big Rocks, Small Rocks)
Approve/Reject voting system with real-time updates
Voting results dashboard


🔑 Data Structures
Feature Object
JSON{  "id": "F-0001",  "title": "Feature Title",  "description": "Detailed description",  "bu": "AI BU",  "year": 2025,  "half": "H1",  "quarter": "Q1",  "type": "Hero Big Rock",  "impact": 9,  "effort": "L",  "rice_score": 285.6,  "competitor_score": 8,  "dependency_details": [    {      "team": "CX BU",      "title": "API Integration",      "description": "Specific need from this team"    }  ],  "dependent_teams": ["CX BU", "Platform BU"],  "prd_file": "filename.pdf",  "mockup_file": "mockup.png",  "submitted_by": "User/Team",  "status": "Under Review",  "created_date": "2024-01-15 10:30:00"}Show more lines
Vote Object
JSON{  "feature_id": {    "approve": 2,    "reject": 1  }}Show more lines

🚀 How to Run
Prerequisites
Shell# Required Python packagesstreamlit>=1.28.0pandas>=2.0.0plotly>=5.0.0openai>=1.0.0   # Optional for AI integrationpython-dotenv>=1.0.0Show more lines
Setup
Shell# Clone the repogit clone <your-repo-url>cd aop-planner-pro# Install dependenciespip install -r requirements.txt# Run the appShow more lines
Access at: http://localhost:8501

🎨 UI/UX Highlights

Color-coded BU badges
Status indicators (Draft, Submitted, Under Review, Approved, Rejected)
Responsive design
Interactive charts & real-time voting
File upload with validation


🔧 Current Functionalities
✅ Implemented:

CRUD for features
Dependency mapping
Multi-BU collaboration & voting
RICE scoring algorithm
Competitor analysis (mock)
Status workflow
File attachments
Data visualization

🔄 Planned:

Real OpenAI integration
Export (CSV, Excel, PDF)
Email notifications
Jira/Asana integration
Authentication & DB persistence


🛠️ Development Notes

All data stored in st.session_state
Reset with “🔄 Reset All” button
Demo data available for quick testing


🚀 Next Steps

Input validation
Autosave during feature creation
Confirmation dialogs for delete
Advanced analytics dashboard
Integration with external tools (Jira, Slack, Calendar)


📦 Deployment Options

Streamlit Cloud (one-click)
Docker container
AWS/GCP/Azure for enterprise
Database migration for production