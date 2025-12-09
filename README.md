# AOP_Planner
📋 AOP Planner Pro - Feature Overview Document
🎯 Project Summary
Annual Operating Plan (AOP) Planning Tool. A centralized platform where Business Units submit feature requests, which are automatically analyzed, prioritized via RICE framework, and collaboratively validated by PM leadership.

🏗️ Application Architecture
Technology Stack
Framework: Streamlit (Python-based, no HTML/CSS needed)
Data Storage: Session State (in-memory, persists during session)
Visualization: Plotly for charts, Pandas for data manipulation
Styling: Custom CSS with Streamlit components
Key Features Implemented
Multi-step workflow for AOP planning
Business Unit-specific feature submission
One-to-many dependency mapping
RICE scoring & competitor analysis
Collaborative PM voting system
Full CRUD operations (Create, Read, Update, Delete)

📱 PAGE-BY-PAGE BREAKDOWN
1. 🏠 HOME PAGE - Dashboard
Purpose: Overview and quick navigation
text
Navigation Elements:
├── Sidebar Navigation
│   ├── Home (Dashboard)
│   ├── Submit New Feature
│   ├── List All Features
│   ├── Analyze & Score
│   └── Collaborate & Vote
│
├── Quick Stats Section
│   ├── Total Features counter
│   ├── Pending Review counter
│   ├── Approved counter
│   └── Hero Big Rocks counter
│
├── Recent Features (8 most recent)
│   ├── Feature title with ID
│   ├── Business Unit badge
│   ├── Timeline (Year, Half, Quarter)
│   ├── Feature type
│   ├── Impact score
│   ├── Status badge
│   └── Action buttons (View, Edit, Delete)
│
└── Visualization Charts
    ├── Features by Business Unit (Pie chart)
    └── Features by Status (Bar chart)
2. 📝 SUBMIT/EDIT PAGE - Feature Creation
Purpose: Create or modify feature requests with detailed dependencies
📋 FORM ELEMENTS:
text
A. BASIC INFORMATION SECTION
├── Feature Title* (text input)
├── Description* (text area, 100px height)
├── Owning Business Unit* (dropdown)
│   └── Options: AI BU, CX BU, EX BU, CE BU, Platform BU
└── Target Year* (dropdown)
    └── Only future years (current+1 to current+5)

B. PLANNING DETAILS SECTION
├── Half-Year* (radio buttons: H1, H2)
├── Quarter* (dropdown - dynamic based on half-year)
│   └── H1: Q1, Q2
│   └── H2: Q3, Q4
├── Feature Type* (dropdown)
│   └── Hero Big Rock, Big Rock, Small Rock
├── Business Impact* (slider 1-10)
└── Effort Estimate* (select slider: XS, S, M, L, XL)

C. DEPENDENT FUNCTIONALITY/NEEDS SECTION
├── One-to-Many Dependency Mapping
│   ├── Dependency 1
│   │   ├── Dependent Team (dropdown - same as BU list)
│   │   ├── Dependency Title (text input)
│   │   └── Dependency Description (text area)
│   ├── [➕ Add Another Dependency] button
│   └── [❌ Remove] button for each additional dependency
│
└── Dependency Summary
    └── Shows grouped dependencies by team

D. ATTACHMENTS SECTION
├── Upload PRD* (file upload - pdf, docx, txt)
└── Upload Mockups (optional - png, jpg, fig, xd)

E. STATUS SELECTION (Edit mode only)
└── Dropdown: Draft, Submitted, Under Review, Approved, Rejected

F. ACTION BUTTONS
├── Submit/Update Feature (primary)
├── Back to Home
└── View All Features
3. 📋 LIST FEATURES PAGE - Feature Management
Purpose: View, filter, and manage all feature requests
text
A. FILTERS SECTION
├── Filter by Business Unit (dropdown with "All" option)
├── Filter by Status (dropdown with "All" option)
├── Filter by Year (dropdown with "All" option)
└── Filter by Type (dropdown with "All" option)

B. FEATURE CARDS (Each feature displays)
├── Feature Title with ID
├── Business Unit badge (color-coded)
├── Timeline information
├── Feature type badge
├── Impact score
├── Status badge with icon
├── Description preview (200 chars)
├── Dependent Teams summary
├── Dependencies organized by team
├── Creation timestamp
└── Action buttons (View, Edit, Delete)

C. NAVIGATION
└── Back to Home button
4. 👁️ VIEW FEATURE PAGE - Detailed View
Purpose: View complete feature details
text
A. HEADER SECTION
├── Feature ID display
├── Status badge
└── Edit button

B. DETAILS IN TWO COLUMNS
├── LEFT COLUMN - Basic Information
│   ├── Title
│   ├── Description (full text)
│   ├── Owning BU with badge
│   ├── Submitted by
│   └── Created date
│
└── RIGHT COLUMN - Planning Details
    ├── Target Year
    ├── Timeline (Half-Quarter)
    ├── Feature Type
    ├── Business Impact
    ├── Effort Estimate
    ├── RICE Score (if calculated)
    └── Competitor Score (if calculated)

C. DEPENDENCIES SECTION
├── Dependent Teams list
├── Total dependency count
└── Dependencies organized by team with details

D. ATTACHMENTS SECTION
├── PRD file status
└── Mockup file status

E. NAVIGATION BUTTONS
├── Back to Home
├── View All Features
└── Delete this Feature
5. 🔍 ANALYZE & SCORE PAGE - Prioritization
Purpose: Run competitor analysis and RICE scoring
text
A. FEATURES OVERVIEW
├── Data table showing all features
├── Columns: ID, Title, BU, Type, Impact, Effort, Status, RICE, Dependent Teams, Dependency Count

B. COMPETITOR ANALYSIS SECTION
├── Competitor selection (dropdown)
├── Analysis depth (Basic/Detailed/Comprehensive slider)
└── Run Competitor Analysis button

C. RICE SCORING SECTION
├── Reach Weight slider (0.0-1.0)
├── Impact Weight slider (0.0-1.0)
├── Confidence Weight slider (0.0-1.0)
├── Effort Weight slider (0.0-1.0)
└── Calculate RICE Scores button

D. RESULTS SECTION
├── Prioritized features table (sorted by RICE score)
├── Color gradient on RICE scores
└── Top 10 Features visualization (bar chart)

E. NAVIGATION
├── Back to Home
└── Next → Collaborate & Vote
6. 🤝 COLLABORATE & VOTE PAGE - PM Approval
Purpose: PM heads review and vote on features
text
A. PM HEAD DASHBOARD
├── Role selection dropdown
│   └── AI BU PM Head, CX BU PM Head, EX BU PM Head, CE BU PM Head, Platform BU PM Head
└── Welcome message with voting rights

B. FEATURE REVIEW BOARD (Tabbed interface)
├── TAB 1: Hero Big Rocks
├── TAB 2: Big Rocks
└── TAB 3: Small Rocks

C. FEATURE VOTING CARD (Each feature)
├── Feature title and details
├── BU badge
├── RICE and Competitor scores
├── Timeline
├── Dependent teams summary
├── Status
├── ✅ Approve button
├── ❌ Reject button
└── Current vote count display

D. VOTING RESULTS SECTION
├── Vote count table
└── Overall voting distribution (pie chart)

E. NAVIGATION
└── Back to Home button

🔑 KEY DATA STRUCTURES
Feature Object Schema
python
{
    "id": "F-0001",                    # Auto-generated ID
    "title": "Feature Title",
    "description": "Detailed description",
    "bu": "AI BU",                     # Owning Business Unit
    "year": 2025,                      # Target Year (future only)
    "half": "H1",                      # H1 or H2
    "quarter": "Q1",                   # Q1-Q4 based on half
    "type": "Hero Big Rock",           # Feature type
    "impact": 9,                       # Business Impact 1-10
    "effort": "L",                     # XS, S, M, L, XL
    "rice_score": 285.6,               # Calculated RICE score
    "competitor_score": 8,             # Competitor analysis score
    "dependency_details": [            # ONE-TO-MANY dependencies
        {
            "team": "CX BU",           # Dependent team
            "title": "API Integration",
            "description": "Specific need from this team"
        },
        # ... more dependencies for same/different teams
    ],
    "dependent_teams": ["CX BU", "Platform BU"],  # Derived from dependencies
    "prd_file": "filename.pdf",        # PRD attachment
    "mockup_file": "mockup.png",       # Mockup attachment
    "submitted_by": "User/Team",
    "status": "Under Review",          # Draft, Submitted, Under Review, Approved, Rejected
    "created_date": "2024-01-15 10:30:00"
}
Vote Object Schema
python
{
    "feature_id": {
        "approve": 2,    # Count of approve votes
        "reject": 1      # Count of reject votes
    }
}

🚀 HOW TO RUN THE APPLICATION
Prerequisites
bash
# Required Python packages
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
openai>=1.0.0        # Optional for AI integration
python-dotenv>=1.0.0
Setup Instructions
Clone/Copy the app.py file
Install dependencies:
bash
pip install -r requirements.txt
Run the application:
bash
streamlit run app.py
Access the app: Open browser to http://localhost:8501
Demo Data
Click "🚀 Load Demo Data" in sidebar
Pre-populates with 3 sample features
Each feature has multiple dependencies demonstrating one-to-many mapping

🎨 UI/UX FEATURES
Visual Design Elements
Color-coded Business Unit badges:
AI BU: 🔵 Blue
CX BU: 🔴 Pink
EX BU: 🟢 Green
CE BU: 🟡 Yellow
Platform BU: 🟣 Purple
Status indicators:
Draft: 🔵 Blue
Submitted: 🟡 Yellow
Under Review: 🟠 Orange
Approved: 🟢 Green
Rejected: 🔴 Red
Card-based layouts with shadows and borders
Responsive design for different screen sizes
Progress indicators for multi-step processes
Interactive Elements
Real-time voting with immediate count updates
Dynamic dependency addition/removal
Live filtering on list pages
Interactive charts with hover details
File upload with validation

🔧 CURRENT FUNCTIONALITIES
✅ IMPLEMENTED
Full CRUD operations for features
One-to-many dependency mapping
Multi-BU collaboration with voting
RICE scoring algorithm
Competitor analysis (mock implementation)
Status workflow (Draft → Submitted → Under Review → Approved/Rejected)
File attachment for PRD and mockups
Comprehensive filtering and search
Data visualization with charts
Responsive UI with professional styling
🔄 IN PROGRESS/PLANNED
Real OpenAI integration for competitor analysis
Export functionality (CSV, Excel, PDF)
Email notifications for status changes
Calendar integration for timeline visualization
Jira/Asana integration for backlog export
User authentication and role-based access
Database persistence (currently session-based)
Advanced analytics dashboard
Team capacity planning
Budget allocation features

🛠️ DEVELOPMENT NOTES
Session State Management
All data stored in st.session_state
Reset with "🔄 Reset All" button
Demo data pre-loaded for quick testing
Key Functions
save_feature() - Handles create/update operations
delete_feature() - Removes features and associated votes
get_dependencies_by_team() - Organizes one-to-many dependencies
render_dependencies_html() - Creates visual dependency display
vote_for_feature() - Manages voting logic and status updates
CSS Customization
All styling in <style> tags within app.py
Custom classes for badges, cards, and status indicators
Responsive design with flexbox layouts

🚀 NEXT STEPS FOR TEAM
Immediate Improvements
Add input validation for all form fields
Implement autosave during feature creation
Add confirmation dialogs for delete operations
Create print-friendly view for features
Add search functionality across all fields
Advanced Features
Real AI integration using OpenAI API
Team capacity planning module
Budget tracking and allocation
Timeline visualization (Gantt charts)
Integration with external tools (Jira, Slack, Calendar)
Deployment Options
Streamlit Cloud (Free, one-click deployment)
Docker container for local deployment
AWS/GCP/Azure for enterprise deployment
Database migration for production use


