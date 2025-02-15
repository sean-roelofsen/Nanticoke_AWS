import dash
from dash import dcc, html, dash_table
import pandas as pd
import boto3
import plotly.express as px

# AWS S3 Configuration
BUCKET_NAME = "your-s3-bucket-name"
FILE_KEY = "cleaned_data.csv"

# Function to Load Data from S3
def load_data():
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    df = pd.read_csv(obj['Body'])
    return df

# Initialize Dash App
app = dash.Dash(__name__)
app.title = "Air Quality Dashboard"

# Load Data
df = load_data()

# Layout
app.layout = html.Div([
    html.H1("Air Quality Monitoring Dashboard"),
    dcc.Interval(id="interval-update", interval=3600*1000, n_intervals=0),  # Update hourly

    dcc.Dropdown(
        id="station-dropdown",
        options=[{"label": i, "value": i} for i in df["Station"].unique()],
        value=df["Station"].unique()[0],
        multi=False,
    ),

    dcc.Graph(id="air-quality-graph"),

    dash_table.DataTable(
        id="data-table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        page_size=15,
        style_table={"overflowX": "auto"}
    )
])

# Callbacks
@app.callback(
    dash.Output("air-quality-graph", "figure"),
    dash.Input("station-dropdown", "value")
)
def update_graph(selected_station):
    filtered_df = df[df["Station"] == selected_station]
    fig = px.line(filtered_df, x="DateTime", y="Measured Value", title=f"Air Quality at {selected_station}")
    return fig

# Run App
if __name__ == "__main__":
    app.run_server(debug=True)
