# Quick Reference Guide

## 🚀 Quick Start Commands

### Windows
```powershell
# Option 1: Run batch file
.\run.bat

# Option 2: Manual
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux
```bash
# Option 1: Run shell script
chmod +x run.sh
./run.sh

# Option 2: Manual
pip install -r requirements.txt
streamlit run app.py
```

---

## 📊 Dashboard Features At-A-Glance

| Feature | Location | Purpose |
|---------|----------|---------|
| **Filter Panel** | Left Sidebar | Multi-select filtering for Roles, Tech, Practices, Phases, Priority, Status |
| **KPI Section** | Top of page | Total Use Cases, Avg ROI, Most Active Phase, AI Readiness Score |
| **Pulse Plot** | Tab 1, Left | AI Utilization by SDLC phase (saturation %) |
| **Status Distribution** | Tab 1, Right | Pie chart breakdown of current status |
| **Implementation Quadrant** | Tab 1, Bottom | Effort vs. ROI vs. Complexity bubble chart |
| **Strategic Heatmap** | Tab 2, Left | Phase vs. ROI Potential density |
| **Priority-Complexity Matrix** | Tab 2, Right | Heatmap of Priority cross Priority vs. Complexity |
| **Cross-Functional Sunburst** | Tab 2, Bottom | Practice → Phase → Technology hierarchy |
| **Detailed Registry** | Tab 3 | Full searchable/sortable table of all use cases |
| **Download CSV** | Tab 3, Bottom | Export filtered data to Excel-compatible format |

---

## 🎨 Color Reference

| Element | Hex | Purpose |
|---------|-----|---------|
| Background | `#0e1117` | Main page background |
| Dark Slate Containers | `#1c2128` | Card/component backgrounds |
| Emerald (Primary) | `#00ff88` | Accents, borders, headings |
| Soft Blue (Secondary) | `#60a5fa` | Alternative accent color |
| Text Primary | `#ffffff` | All text |
| Not Started | `#6b7280` | Status color (gray) |
| In Progress | `#f59e0b` | Status color (amber) |
| Completed | `#10b981` | Status color (green) |
| On Hold | `#ef4444` | Status color (red) |
| Cancelled | `#6b7280` | Status color (gray) |

---

## 📐 Data Mapping Reference

### Effort Estimate → Days
| Input | Output |
|-------|--------|
| XS (Extra Small) | 1 day |
| S (Small) | 3 days |
| M (Medium) | 10 days |
| L (Large) | 25 days |
| XL (Extra Large) | 45 days |

### ROI Potential → Score (1-4)
| Input | Output |
|-------|--------|
| Low | 1 |
| Medium | 2 |
| High | 3 |
| Very High | 4 |

### Complexity → Score (1-3)
| Input | Output |
|-------|--------|
| Low | 1 |
| Medium | 2 |
| High | 3 |

---

## 🔧 Configuration Files

### `requirements.txt`
Lists all Python dependencies with pinned versions

**To update packages:**
```bash
pip install -r requirements.txt --upgrade
```

### `.streamlit/config.toml`
Streamlit configuration for theme, server settings, client behavior

**Key Settings:**
```toml
[theme]
primaryColor = "#00ff88"        # Emerald
backgroundColor = "#0e1117"     # Dark slate
secondaryBackgroundColor = "#1c2128"  # Darker slate
textColor = "#ffffff"           # White

[client]
toolbarMode = "minimal"         # Hide Streamlit toolbar in prod

[server]
maxUploadSize = 200             # Max file upload in MB
headless = true                 # Run without browser launch
```

---

## 📁 Mock Data Structure

The app auto-generates 110 records with this structure:

```
Use_Case_ID: "UC-001" to "UC-110"
Use_Case_Name: Realistic AI project names
SDLC_Phase: One of 11 phases (Requirements, Architecture, Design, etc.)
Priority: Low, Medium, High, Critical
Status: Not Started, In Progress, Completed, On Hold, Cancelled
Effort_Estimate: XS, S, M, L, XL
ROI_Potential: Low, Medium, High, Very High
Complexity: Low, Medium, High
Role: "Data Scientist;#ML Engineer;#Product Owner" (;# delimited)
Technology: "Python;#TensorFlow;#Azure ML" (;# delimited)
Practice_Applicability: "Predictive Analytics;#NLP" (;# delimited)
Start_Date: Random date in last 400 days
Expected_Completion: Random date in next 365 days
Owner: "Manager_0" to "Manager_14"
```

---

## 🔍 Filter Logic

### How Filters Work
1. **Sidebar Selection**: You select values for each filter
2. **Cumulative Application**: ALL selected filters apply (AND logic)
3. **Multi-Value Matching**: For Role/Tech/Practice, matches any element in the delimited list
4. **Non-Double-Counting**: Same use case won't appear twice even if it has multiple matching values

### Filter Application Order
1. Extract exploded dataframe (multi-value columns split)
2. Apply Role filter
3. Apply Technology filter
4. Apply Practice Applicability filter
5. Apply SDLC Phase filter
6. Apply Priority filter
7. Apply Status filter
8. Get Use_Case_IDs matching all filters
9. Return original (non-exploded) records for those IDs

---

## 📈 Visualization Interpretation Guide

### The Pulse Plot (Tab 1)
**Shows**: AI Utilization (saturation) per SDLC phase
**Formula**: (Completed + In Progress) / Total Use Cases in Phase
**Interpretation**:
- **High saturation (80%+)**: Phase is busy, consider load balancing
- **Low saturation (<20%)**: Phase has capacity for more work
- **Color Gradient**: Gray (low) → Blue (medium) → Emerald (high)

### The Strategic Heatmap (Tab 2)
**Shows**: Which phases have high-ROI opportunities
**Interpretation**:
- **Bright spots**: Phase with many high-ROI use cases
- **Strategy**: Prioritize work in high-ROI phases
- **Planning**: Dark areas = potential gaps to address

### The Implementation Quadrant (Tab 2)
**Shows**: Effort vs. ROI vs. Complexity trade-offs
**Axes**:
- **X (Effort)**: Log scale (1-45 days)
- **Y (ROI)**: 1-4 numeric score
- **Size (Complexity)**: Bubble size = complexity level
- **Color (Status)**: Status indicated by color

**Key Zones**:
- **Top-Left (Green Zone)**: High ROI, Low effort, Low complexity = QUICK WINS
- **Top-Right (Invest Zone)**: High ROI but effortful/complex = Strategic investments
- **Bottom-Left (Reconsider)**: Low ROI, low effort = Does it align with strategy?
- **Bottom-Right (Red Zone)**: Low ROI, high effort = Avoid unless mandatory

### The Cross-Functional Sunburst (Tab 2)
**Shows**: How practices, phases, and technologies interrelate
**Navigation**:
- **Click inner ring**: Drill down to specific practice area
- **Click center**: Reset to root view
- **Hover**: See exact counts
- **Interpretation**: Larger segments indicate higher adoption/focus

---

## 💾 Exporting & Integration

### Download as CSV
1. Go to **Tab 3 (Detailed Registry)**
2. Apply desired filters
3. Click **"📥 Download Filtered Data (CSV)"** button
4. Opens as `ai_use_cases_YYYYMMDD.csv`

### Open in Excel
1. Download CSV from app
2. Open Excel
3. File → Open → Select downloaded CSV
4. Excel may auto-format with column headers and freeze panes

### Use Your Own Data
1. Prepare CSV with required 14 columns
2. In `app.py` line 1113, replace:
   ```python
   st.session_state.data = generate_catalogue_data(n_records=110)
   ```
   with:
   ```python
   st.session_state.data = pd.read_csv('path/to/your/file.csv')
   ```
3. Run app with: `streamlit run app.py`

---

## 🆘 Troubleshooting

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| App won't start | Missing packages | Run `pip install -r requirements.txt` |
| Blank charts | Empty filtered dataset | Clear filters or adjust criteria |
| Colors look wrong | Theme not applied | Restart Streamlit: `Ctrl+C`, then `streamlit run app.py` |
| Filters do nothing | Delimiter mismatch | Verify `;#` delimiter in data (no spaces) |
| "Python not found" | Python not installed | Install Python 3.8+ from python.org |
| "ModuleNotFoundError" | Package not installed | Run pip install with specific package name |
| Slow performance | Large dataset + complex viz | Reduce visible data or optimize hardware |

---

## 📞 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Plotly Docs**: https://plotly.com/python/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **Python Docs**: https://docs.python.org/3/

---

## 🎯 Common Use Cases

### Scenario 1: "Find quick wins"
1. Open **Tab 1: Implementation Quadrant**
2. Look for bubbles in **top-left** (High ROI, Low effort)
3. Filter by Status = "Not Started" or "In Progress"
4. Review and prioritize

### Scenario 2: "Identify bottleneck phases"
1. Open **Tab 1: Pulse Plot**
2. Look for phases with **high saturation** (>80%)
3. Using sidebar, filter to show use cases in those phases
4. Determine if resources can be added or work deferred

### Scenario 3: "Explore technology adoption"
1. Open **Tab 2: Cross-Functional Sunburst**
2. Click on specific Practice Area segment
3. See which Technologies and Phases are involved
4. Use to identify training needs or tool consolidation

### Scenario 4: "Budget allocation planning"
1. Filter by **Priority = Critical**
2. Analyze **Effort_Days** and **Complexity** in **Implementation Quadrant**
3. Sum total effort for budgeting
4. Export to CSV for presentation

---

**Version**: 1.0.0  
**Last Updated**: March 2026
