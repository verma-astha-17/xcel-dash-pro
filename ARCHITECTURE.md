# Technical Architecture & Advanced Customization Guide

## Table of Contents
1. [Project Structure](#project-structure)
2. [Code Architecture](#code-architecture)
3. [Data Flow](#data-flow)
4. [Customization Guide](#customization-guide)
5. [Advanced Features](#advanced-features)
6. [Performance Optimization](#performance-optimization)

---

## Project Structure

```
d:\EmpDash\
├── app.py                          # Main Streamlit application (3,200+ lines)
├── requirements.txt                # Python dependencies
├── README.md                       # User-facing documentation
├── ARCHITECTURE.md                 # This file
├── run.sh                          # Linux/Mac quick-start script
├── run.bat                         # Windows quick-start script
└── .streamlit/
    └── config.toml                 # Streamlit configuration (theme, server settings)
```

## Code Architecture

### 1. Configuration Layer (Lines 1-50)
Defines all constants, color schemes, and mappings:
- **Effort Mapping**: XS/S/M/L/XL → 1/3/10/25/45 days
- **ROI Mapping**: Low/Medium/High/Very High → 1/2/3/4
- **Complexity Mapping**: Low/Medium/High → 1/2/3
- **Color Palette**: Deep Slate & Cyber Emerald theme
- **SDLC Phases**: 11 phases (Requirements through Support)

### 2. Data Generation Layer (Lines 50-150)
**Function**: `generate_catalogue_data(n_records=110)`
- Generates realistic 110-record mock dataset
- Uses nested comprehensions for multi-valued columns
- Creates delimited Role, Technology, Practice_Applicability columns

**Why it's important**:
- App is immediately runnable without external data
- Demonstrates expected data structure for custom data integration
- Seeded with `np.random.seed(42)` for reproducibility

### 3. Data Processing Layer (Lines 150-350)
Four critical functions:

#### a) `explode_multivalued_columns(df, delimiter=';#')`
- **Purpose**: Split multi-valued columns without double-counting records
- **Logic**: 
  1. Creates expanded dataframe for analysis
  2. Keeps original dataframe intact
  3. Returns dict with both versions
- **Use Case**: Filtering by Role/Technology without artificial record multiplication

#### b) `map_*_to_*()` Functions
Three mapping functions convert categorical to numeric:
- Used in `enrich_dataframe()` for numeric computations
- Enable quantitative analysis in visualizations

#### c) `enrich_dataframe(df)`
- **Purpose**: Add calculated columns
- **New Columns**:
  - `Effort_Days`: Numeric conversion of Effort_Estimate
  - `ROI_Score`: Numeric conversion of ROI_Potential
  - `Complexity_Score`: Numeric conversion of Complexity
  - `Readiness_Score`: 0-100 AI readiness metric

#### d) `calculate_phase_saturation(df)`
- **Formula**: (Completed + In Progress) / Total per Phase
- **Output**: DataFrame with Phase, Total, Active, Saturation columns
- **Business Logic**: Shows which SDLC phases are saturated with active work

### 4. Visualization Layer (Lines 350-800)
Five visualization functions using Plotly:

#### a) `create_pulse_plot(saturation_df)`
- **Chart Type**: Horizontal bar chart
- **X-Axis**: Saturation percentage (0-100%)
- **Y-Axis**: SDLC phases (sorted by saturation)
- **Color Scale**: Gray → Blue → Emerald (gradient)
- **Key Feature**: Shows which phases need more capacity

#### b) `create_strategic_heatmap(df_exploded)`
- **Chart Type**: 2D heatmap
- **X-Axis**: ROI Potential (Low/Medium/High/Very High)
- **Y-Axis**: SDLC phases
- **Values**: Count of use cases
- **Key Feature**: Identifies ROI-rich phases for resource focus

#### c) `create_implementation_quadrant(df_enriched)`
- **Chart Type**: Bubble scatter plot
- **X-Axis**: Effort (days, logarithmic scale)
- **Y-Axis**: ROI Score (1-4)
- **Bubble Size**: Complexity Score (1-3)
- **Color**: Status (Not Started/In Progress/Completed/On Hold/Cancelled)
- **Key Feature**: Identifies high-ROI, low-effort quick wins

#### d) `create_cross_functional_matrix(df_exploded)`
- **Chart Type**: Sunburst diagram
- **Hierarchy**: Practice Area → SDLC Phase → Technology
- **Values**: Aggregated use case counts
- **Key Feature**: Shows technology adoption across practices

#### e) Supporting Visualizations
- Status distribution pie chart (inline in Tab 1)
- Priority vs. Complexity heatmap (inline in Tab 2)

### 5. Styling Layer (Lines 800-950)
**Function**: `inject_custom_css()`
- Injects 200+ lines of custom CSS
- Implements glassmorphism effects (semi-transparent containers with blur)
- Custom scrollbar styling
- Button hover animations with glow effects
- Responsive grid layouts

**Key Styling Features**:
```css
/* Glassmorphism */
backdrop-filter: blur(10px);
background: rgba(28, 33, 40, 0.6);
border: 1px solid rgba(0, 255, 136, 0.2);

/* Emerald glow on hover */
box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
```

### 6. Application Layer (Lines 950+)
**Function**: `main()`
- Streamlit page configuration
- Session state management
- Sidebar filter UI
- Three-tab layout
- KPI metrics display
- Data export functionality

---

## Data Flow

```
Step 1: Initialize
  └─→ generate_catalogue_data(110)
      └─→ Create 110-row mock dataset

Step 2: Enrich
  └─→ enrich_dataframe(df)
      └─→ Add Effort_Days, ROI_Score, Complexity_Score, Readiness_Score

Step 3: Process
  ├─→ explode_multivalued_columns()
  │   └─→ Create expanded dataset for filtering (no double-counting)
  └─→ calculate_phase_saturation()
      └─→ Compute utilization per SDLC phase

Step 4: Filter (Sidebar)
  └─→ Apply user-selected filters to exploded dataset
      └─→ Get matching Use_Case_IDs
      └─→ Return filtered original records

Step 5: Visualize
  ├─→ Tab 1: Pulse Plot + Status Pie + Implementation Quadrant
  ├─→ Tab 2: Strategic Heatmap + Priority-Complexity + Sunburst
  └─→ Tab 3: Detailed table + expandable full view + CSV export
```

---

## Customization Guide

### 1. Add New SDLC Phases

**File**: `app.py` lines 23-26

```python
SDLC_PHASES = [
    'Requirements', 'Architecture', 'Design', 'Development', 
    'Testing', 'Deployment', 'Maintenance', 'Operations',
    'Optimization', 'Retirement', 'Support',
    'YOUR_NEW_PHASE',  # Add here
]
```

Update `generate_catalogue_data()` to include new phase in random selection.

### 2. Change Color Scheme

**File**: `app.py` lines 28-38

```python
COLOR_BG = '#yourHexColor'           # Main background
COLOR_EMERALD = '#yourHexColor'      # Primary accent
COLOR_BLUE = '#yourHexColor'         # Secondary accent
COLOR_DARK_SLATE = '#yourHexColor'   # Card backgrounds
COLOR_TEXT_PRIMARY = '#yourHexColor' # Text color
```

Also update `.streamlit/config.toml` (lines 1-5) for Streamlit theme:

```toml
[theme]
primaryColor = "#yourHexColor"
backgroundColor = "#yourHexColor"
textColor = "#yourHexColor"
```

### 3. Adjust Metric Mappings

**File**: `app.py` lines 10-12

```python
# Change effort days
EFFORT_MAPPING = {'XS': 2, 'S': 5, 'M': 15, 'L': 30, 'XL': 50}

# Change ROI scale (3-point instead of 4-point)
ROI_MAPPING = {'Low': 1, 'Medium': 2, 'High': 3}
```

### 4. Modify AI Readiness Score Formula

**File**: `app.py` lines 280-305

Current formula (total = 100%):
- Average ROI: 40%
- Completion rate: 30%
- Complexity management: 20%
- Pipeline momentum: 10%

Example: Increase ROI weight to 50%

```python
def calculate_ai_readiness_score(df_enriched):
    avg_roi = (df_enriched['ROI_Score'].mean() / 4) * 50  # Changed from 40
    completion_rate = (len(df_enriched[...]) / len(df_enriched)) * 25  # Changed from 30
    complexity_factor = ((3 - df_enriched['Complexity_Score'].mean()) / 3) * 15  # Changed from 20
    momentum = (len(df_enriched[...]) / len(df_enriched)) * 10  # Unchanged
    return np.clip(avg_roi + completion_rate + complexity_factor + momentum, 0, 100)
```

### 5. Add New Visualization Tab

**File**: `app.py` lines 1200+

```python
# In main(), add to tab creation:
tab1, tab2, tab3, tab4 = st.tabs([
    '📈 Executive Portfolio',
    '🔥 Strategic Heatmaps',
    '📋 Detailed Registry',
    '🆕 Your New Tab'
])

# Add new tab content:
with tab4:
    st.markdown('### Your Custom Analysis')
    # Create your visualization here
    fig = your_custom_plot_function(df_filtered)
    st.plotly_chart(fig, use_container_width=True)
```

### 6. Custom Filter Categories

**File**: `app.py` lines 1070-1100

Add new filter in sidebar:

```python
custom_filter_options = df['Your_Column'].unique().tolist()
filtered_custom = st.sidebar.multiselect(
    '🎯 Your Category',
    options=custom_filter_options,
    default=custom_filter_options[:3],
    key='filter_custom'
)

# Apply filter:
if filtered_custom:
    df_filtered = df_filtered[
        df_filtered['Your_Column'].isin(filtered_custom)
    ]
```

### 7. Integrate Your Own CSV Data

**File**: `app.py` lines 1110-1115 (in `main()`)

Replace:
```python
st.session_state.data = generate_catalogue_data(n_records=110)
```

With:
```python
st.session_state.data = pd.read_csv('path/to/your/file.csv')
```

**Important**: Ensure your CSV has these 14 columns:
- Use_Case_ID, Use_Case_Name, SDLC_Phase, Priority, Status
- Effort_Estimate, ROI_Potential, Complexity
- Role, Technology, Practice_Applicability (use `;#` delimiter)
- Start_Date, Expected_Completion, Owner

---

## Advanced Features

### 1. Session State Management
Streamlit's `st.session_state` caches processed data to prevent recalculation:

```python
if 'data' not in st.session_state:
    st.session_state.data = generate_catalogue_data()
    st.session_state.data_enriched = enrich_dataframe(...)
    st.session_state.data_exploded = explode_multivalued_columns(...)
```

**Benefit**: Filtering doesn't re-run data generation/enrichment (fast UX)

### 2. Multi-Select Cumulative Filtering
Filters work with AND logic (intersection), not OR:
- Select Role A, Role B → Show use cases with BOTH roles
- To change to OR logic, modify filter application (line 1135):

```python
# Current (AND):
if filtered_roles:
    df_filtered_exploded = df_filtered_exploded[
        df_filtered_exploded['Role'].isin(filtered_roles)
    ]

# Alternative (OR):
# Keep union of records instead of intersection
```

### 3. Plotly Interactivity
All Plotly charts have built-in features:
- **Hover**: Detailed tooltips
- **Click Legend**: Toggle data series on/off
- **Zoom/Pan**: Drag to zoom, double-click to reset
- **Download**: Camera icon to save as PNG
- **Colorscale**: Interactive colorbar for heatmaps

### 4. Error Handling
Graceful degradation for edge cases:
- Empty dataframes: Charts show empty state
- Missing columns: Error messages in UI
- Null values: Excluded from calculations automatically
- Division by zero: Wrapped with `if len(df) > 0` checks

---

## Performance Optimization

### 1. Caching Strategy
```python
# Don't do this (recalculates every filter change):
saturation = calculate_phase_saturation(df_filtered)

# Do this (caches initial calculation):
if 'saturation' not in st.session_state:
    st.session_state.saturation = calculate_phase_saturation(df)
```

### 2. Large Dataset Handling
For 1000+ records:
1. Enable Plotly's WebGL mode for scatter plots
2. Reduce marker opacity to show overlaps
3. Use aggregation (heatmaps/histograms instead of scatter)
4. Paginate the detailed registry table

### 3. Streamlit Column Selection
Use `st.columns()` efficiently:
```python
col1, col2 = st.columns(2)  # 50% width each
col1, col2, col3 = st.columns([1, 2, 1])  # Weighted widths
```

### 4. CSS Optimization
The injected CSS is minified with inline styles. Use `st.cache_resource` for heavy computations:

```python
@st.cache_resource
def expensive_function():
    return result
```

---

## Troubleshooting

### Issue: Filters not properly excluding records
**Cause**: Multi-valued column delimiters don't match `;#`
**Solution**: Verify exact delimiter in data, update `MULTI_VALUED_DELIMITER`

### Issue: Plotly charts rendering slowly
**Cause**: Large dataset + many hover details
**Solution**: Reduce hover template complexity, use WebGL mode

### Issue: AI Readiness Score always 50
**Cause**: Weights in formula don't sum to 100
**Solution**: Verify weights (currently 40+30+20+10=100)

### Issue: CSV upload fails
**Cause**: Column name mismatch or missing delimiter
**Solution**: Ensure 14 required columns and `;#` delimiters in multi-value cols

---

## Future Enhancement Ideas

1. **Real-time Data Integration**: Connect to REST API for live updates
2. **Role-Based Access Control**: Different dashboards per user role
3. **Predictive Analytics**: ML model to forecast completion dates
4. **Notification System**: Alert when use cases exceed time/budget thresholds
5. **Collaboration Features**: Comments, approvals, status updates
6. **Export Formats**: PDF reports, Excel dashboards, Power BI integration
7. **Mobile App**: React Native companion app
8. **Dark/Light Mode Toggle**: User theme preference

---

**Last Updated**: March 2026  
**Maintained by**: Senior Full-Stack AI Engineer
