import pandas as pd
import panel as pn
import plotly.express as px
import os

pn.extension('plotly', sizing_mode='stretch_both', theme='dark')

# Load data
try:
    df = pd.read_csv("cleaned_africa_health_data.csv")
except FileNotFoundError:
    raise FileNotFoundError("cleaned_africa_health_data.csv not found. Ensure the file is in the working directory.")

# Standardize country names to ISO_A3 codes for Plotly
country_map = {
    'Algeria': 'DZA', 'Angola': 'AGO', 'Benin': 'BEN', 'Botswana': 'BWA', 'Burkina Faso': 'BFA',
    'Burundi': 'BDI', 'Cabo Verde': 'CPV', 'Cameroon': 'CMR', 'Central African Republic': 'CAF',
    'Chad': 'TCD', 'Comoros': 'COM', 'Democratic Republic Of The Congo': 'COD',
    'Republic Of The Congo': 'COG', 'Djibouti': 'DJI', 'Egypt': 'EGY', 'Equatorial Guinea': 'GNQ',
    'Eritrea': 'ERI', 'Eswatini': 'SWZ', 'Ethiopia': 'ETH', 'Gabon': 'GAB', 'Gambia': 'GMB',
    'Ghana': 'GHA', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB', 'Ivory Coast': 'CIV',
    'Kenya': 'KEN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY', 'Madagascar': 'MDG',
    'Malawi': 'MWI', 'Mali': 'MLI', 'Mauritania': 'MRT', 'Mauritius': 'MUS', 'Morocco': 'MAR',
    'Mozambique': 'MOZ', 'Namibia': 'NAM', 'Niger': 'NER', 'Nigeria': 'NGA', 'Rwanda': 'RWA',
    'Sao Tome And Principe': 'STP', 'Senegal': 'SEN', 'Seychelles': 'SYC', 'Sierra Leone': 'SLE',
    'Somalia': 'SOM', 'South Africa': 'ZAF', 'South Sudan': 'SSD', 'Sudan': 'SDN',
    'Tanzania': 'TZA', 'Togo': 'TGO', 'Tunisia': 'TUN', 'Uganda': 'UGA', 'Zambia': 'ZMB',
    'Zimbabwe': 'ZWE', 'Western Sahara': 'ESH'
}
df['iso_a3'] = df['country'].map(country_map)

# Filter African countries only
african_iso_codes = list(country_map.values())
df = df[df['iso_a3'].isin(african_iso_codes)]

# Indicator selector widget
indicator = pn.widgets.Select(
    name='Select Indicator',
    options=[
        'vaccination_rate',
        'access_to_water',
        'malaria_prevalence',
        'hiv_prevalence',
        'access_to_sanitation'
    ],
    value='vaccination_rate',
    width_policy='fit'
)

# Dynamic KPI panel
@pn.depends(indicator)
def kpi_summary(indicator):
    if indicator not in df.columns:
        return pn.pane.Markdown(f"**Indicator `{indicator}` not found in data.**")
    
    top = df[['country', indicator]].dropna().sort_values(by=indicator, ascending=False).head(3)
    markdown = f"""
### 🔍 Top 3 Countries by {indicator.replace('_', ' ').title()}  
{top.to_markdown(index=False)}
"""
    return pn.pane.Markdown(markdown, sizing_mode='stretch_both')

# Choropleth map
@pn.depends(indicator)
def choropleth_panel(indicator):
    try:
        fig = px.choropleth(
            df,
            locations='iso_a3',
            color=indicator,
            hover_name='country',
            hover_data={indicator: ':.2f', 'region': True} if 'region' in df.columns else {indicator: ':.2f'},
            color_continuous_scale='Blues',
            title=indicator.replace('_', ' ').title(),
            scope='africa',
            height=400
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=50, b=10),
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='rgba(0,0,0,0)',
                landcolor='lightgray',
                showcountries=True,
                countrycolor='white'
            )
        )
        return pn.pane.Plotly(fig, sizing_mode='stretch_both', height=400)
    except Exception as e:
        return pn.pane.Markdown(f"Error rendering map: {str(e)}")

# Scatter plot
@pn.depends(indicator)
def scatter_panel(indicator):
    if 'healthcare_facilities' not in df.columns:
        return pn.pane.Markdown("**Missing 'healthcare_facilities' column in dataset.**")

    try:
        fig = px.scatter(
            df,
            x='healthcare_facilities',
            y=indicator,
            color='region' if 'region' in df.columns else None,
            size='vaccination_rate' if 'vaccination_rate' in df.columns else None,
            hover_name='country',
            hover_data={col: ':.2f' for col in ['healthcare_facilities', indicator] if col in df.columns},
            title=f'Healthcare Facilities vs {indicator.replace("_", " ").title()}',
            color_discrete_sequence=px.colors.qualitative.Safe,
            height=400
        )
        fig.update_layout(
            xaxis_title='Healthcare Facilities',
            yaxis_title=indicator.replace('_', ' ').title(),
            legend_title='Region',
            margin=dict(l=10, r=10, t=50, b=10)
        )
        fig.update_traces(marker=dict(sizemin=5, sizeref=0.05))
        return pn.pane.Plotly(fig, sizing_mode='stretch_both', height=400)
    except Exception as e:
        return pn.pane.Markdown(f"Error rendering scatter plot: {str(e)}")

# Data table
table = pn.widgets.DataFrame(
    df,
    name="Data Table",
    autosize_mode='fit_columns',
    sizing_mode='stretch_both',
    height=400
)

# Download button
def file_download_callback():
    return df.to_csv(index=False).encode()

download_button = pn.widgets.FileDownload(
    callback=file_download_callback,
    filename='health_data.csv',
    button_type='primary',
    label='Download Data',
    width_policy='fit'
)

# Layout sections
top_left = pn.Column(
    "## Filter & KPIs",
    indicator,
    kpi_summary,
    sizing_mode='stretch_width',
    max_width=350
)

top_right = pn.Column(
    "## Map View",
    choropleth_panel,
    sizing_mode='stretch_both'
)

bottom_left = pn.Column(
    "## Scatter Plot",
    scatter_panel,
    sizing_mode='stretch_both'
)

bottom_right = pn.Column(
    "## Data Table",
    table,
    download_button,
    sizing_mode='stretch_both'
)

layout = pn.GridSpec(nrows=2, ncols=2, sizing_mode='stretch_both')
layout[0, 0] = top_left
layout[0, 1] = top_right
layout[1, 0] = bottom_left
layout[1, 1] = bottom_right

# Serve the dashboard
pn.serve(layout, title="Africa Health Dashboard", port=5000)
