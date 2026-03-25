<<<<<<< HEAD
# 🚀 AI Use Case Portfolio Dashboard

A **production-ready Streamlit application** for Project Managers and executives to track AI adoption, ROI, and delivery status across 110 use cases spanning 11 SDLC phases.

## 📋 Features

### Data Engineering
- **Multi-Value Handling**: Automatic "explosion" of multi-delimited columns (Role, Technology, Practice Applicability) using `;#` delimiter
- **Metric Mapping**: 
  - Effort Estimate (XS→1, S→3, M→10, L→25, XL→45 days)
  - ROI Potential (Low→1, Medium→2, High→3, Very High→4)
  - Complexity (Low→1, Medium→2, High→3)
- **Phase Saturation Calculation**: Compares active use cases vs. total per SDLC phase
- **AI Readiness Scoring**: Weighted metric combining ROI, completion rate, complexity, and momentum

### Visualizations (Plotly)
1. **The Pulse Plot**: Horizontal bar chart of AI utilization across all SDLC phases
2. **The Strategic Heatmap**: 2D density plot of Phase vs. ROI Potential
3. **The Implementation Quadrant**: Bubble chart (Effort vs. ROI vs. Complexity, colored by Status)
4. **The Cross-Functional Matrix**: Sunburst diagram (Practice Area → SDLC Phase → Technology)
5. **Additional Charts**: Status distribution pie, Priority vs. Complexity heatmap

### User Interface
- **Theme**: Deep Slate & Cyber Emerald with glassmorphic effects
  - Background: `#0e1117`
  - Accents: `#00ff88` (Emerald) and `#60a5fa` (Soft Blue)
- **Advanced Filtering**: Multi-select filters for Roles, Technologies, Practice Areas, Phases, Priority, and Status
- **Executive KPIs**: Total use cases, Average ROI, Most Active Phase, AI Readiness Score
- **Three Main Tabs**:
  - 📈 Executive Portfolio (Pulse plot, status distribution, implementation quadrant)
  - 🔥 Strategic Heatmaps (Phase-ROI matrix, priority-complexity matrix, cross-functional sunburst)
  - 📋 Detailed Registry (Searchable/sortable table with download capability)

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone or Download
```bash
cd d:\EmpDash
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📊 Mock Data

The application includes a built-in **mock data generator** that creates 110 realistic AI use case records. Launch the app to auto-generate this data—no CSV upload required. The data includes:

- ✅ 110 use case records
- ✅ All 11 SDLC phases (Requirements, Architecture, Design, Development, Testing, Deployment, Maintenance, Operations, Optimization, Retirement, Support)
- ✅ Multi-valued Role, Technology, and Practice Applicability columns with `;#` delimiters
- ✅ Realistic effort, ROI, complexity, and status distributions

## 🎯 How to Use

### 1. **Filtering** (Left Sidebar)
- Use multi-select filters to drill down into specific roles, technologies, practice areas, SDLC phases, priorities, and statuses
- Filters work cumulatively without double-counting use cases

### 2. **Executive Portfolio** (Tab 1)
- View **The Pulse Plot** to understand which SDLC phases are saturated
- Check **Status Distribution** to see completion rates
- Analyze **The Implementation Quadrant** to find high-ROI, low-effort opportunities

### 3. **Strategic Heatmaps** (Tab 2)
- Identify **Phase-ROI patterns** to allocate resources effectively
- Cross-reference **Priority vs. Complexity** to understand risk/effort trade-offs
- Explore the **Cross-Functional Matrix** to see technology and practice adoption

### 4. **Detailed Registry** (Tab 3)
- Browse all filtered use cases in a comprehensive table
- Sort by any column (default: Readiness Score)
- Download filtered data as CSV for further analysis

## 📐 Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| `Use_Case_ID` | string | Unique identifier (UC-001, UC-002, etc.) |
| `Use_Case_Name` | string | Descriptive use case title |
| `SDLC_Phase` | enum | One of 11 SDLC phases |
| `Priority` | enum | Low, Medium, High, Critical |
| `Status` | enum | Not Started, In Progress, Completed, On Hold, Cancelled |
| `Effort_Estimate` | enum | XS, S, M, L, XL (mapped to 1-45 days) |
| `ROI_Potential` | enum | Low, Medium, High, Very High (mapped to 1-4) |
| `Complexity` | enum | Low, Medium, High (mapped to 1-3) |
| `Role` | string | Semi-colon delimited list of roles |
| `Technology` | string | Semi-colon delimited list of technologies |
| `Practice_Applicability` | string | Semi-colon delimited list of practices |
| `Start_Date` | date | Project start date |
| `Expected_Completion` | date | Target completion date |
| `Owner` | string | Project manager/owner |

### Calculated Columns
| Column | Description |
|--------|-------------|
| `Effort_Days` | Numeric days mapped from Effort_Estimate |
| `ROI_Score` | Numeric 1-4 scale for ROI Potential |
| `Complexity_Score` | Numeric 1-3 scale for Complexity |
| `Readiness_Score` | 0-100 weighted AI Readiness metric |

## 🎨 Customization

### Change Color Scheme
Edit the constants at the top of `app.py`:
```python
COLOR_BG = '#0e1117'           # Dark slate background
COLOR_EMERALD = '#00ff88'      # Primary accent
COLOR_BLUE = '#60a5fa'         # Secondary accent
```

### Adjust Effort/ROI/Complexity Mappings
Modify the mapping dictionaries:
```python
EFFORT_MAPPING = {'XS': 1, 'S': 3, 'M': 10, 'L': 25, 'XL': 45}
ROI_MAPPING = {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
COMPLEXITY_MAPPING = {'Low': 1, 'Medium': 2, 'High': 3}
```

### Update AI Readiness Score Formula
Modify the `calculate_ai_readiness_score()` function to adjust weighting:
```python
# Current weights:
# - Average ROI: 40%
# - Completion rate: 30%
# - Complexity management: 20%
# - Active pipeline momentum: 10%
```

## 🔄 Integration with Your Data

To use your own CSV data instead of mock data:

1. Replace the `generate_catalogue_data()` function call in `main()`:
```python
# Replace this:
df = generate_catalogue_data(n_records=110)

# With your own:
df = pd.read_csv('your_data.csv')
```

2. Ensure your CSV matches the structure (14 columns as described above)

3. The app automatically detects and handles multi-valued columns with `;#` delimiters

## 🚨 Error Handling

The application includes robust error handling for:
- Empty or missing data
- Invalid categorical values
- Mismatched column names
- Null/NaN values in calculations

All calculations gracefully handle edge cases without crashing.

## 📈 Performance Notes

- **Optimized for 100-1000 use cases**: Fast filtering and rendering
- **Session state**: Uses Streamlit session state to cache computed data (no recalculation on refilter)
- **Plotly rendering**: All charts rendered client-side for smooth interactivity

## 🔐 Security & Best Practices

- No external API calls (fully offline)
- No sensitive data exposure
- Uses pandas for secure data handling
- CSS injection uses only safe styling (no script injection)

## 📝 License

This project is provided as-is for internal use.

## 💡 Support & Troubleshooting

### Issue: App won't start
**Solution**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Charts not rendering
**Solution**: Clear browser cache and refresh. Plotly may need time to load on first run.

### Issue: Filters aren't working
**Solution**: Ensure delimiters in multi-value columns are exactly `;#` (no spaces)

### Issue: Need to change mock data
**Solution**: Edit the `generate_catalogue_data()` function or replace with your own data source

## 🤝 Contributing

To extend the dashboard:
1. Add new SDLC phases to `SDLC_PHASES`
2. Create new visualization functions following the existing Plotly pattern
3. Add new filters to the sidebar
4. Update the README with new features

---

**Created by**: Senior Full-Stack AI Engineer & Lead UX Architect  
**Last Updated**: March 2026
=======
# xcel-dash-pro
This Proof of Concept (POC) demonstrates the automated generation of user interfaces (UI) by leveraging Excel-based data sources that contain multiple interrelated tables. The solution showcases how Copilot capabilities and agentic frameworks can interpret structured data, understand relationships across tables, and dynamically generating the UI.
>>>>>>> 3c4b4aaa41a7fc31e0055e31e20bf668e6757bd1
