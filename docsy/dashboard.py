from flask import Flask, render_template
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import sqlite3
import datetime

server = Flask(__name__)

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/dashboard/",
)


def serve_layout():
    def fetch_data(query):
        conn = sqlite3.connect("file:data/db.sqlite?mode=ro", uri=True)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # Query to get event data
    df = fetch_data("SELECT created_on, title FROM events")

    # Convert created_on to datetime
    df["created_on"] = pd.to_datetime(df["created_on"])

    # Aggregate the data by minute to count events
    df["minute"] = df["created_on"].dt.floor("min")
    df_timeline = df.groupby("minute").size().reset_index(name="event_count")

    # Create a timeline chart
    fig_timeline = px.line(
        df_timeline, x="minute", y="event_count", title="Number of Events Over Time"
    )

    # Aggregate data by title to count events
    df_title = df.groupby("title").size().reset_index(name="event_count")

    # Create a bar chart for event count by title
    fig_bar = px.bar(
        df_title, x="title", y="event_count", title="Number of Events by Title"
    )

    return html.Div(
        children=[
            html.H1(children="Event Dashboard"),
            html.Div(
                children=[
                    "This dashboard shows a few metrics about user interactions with Docsy.",
                    "It was last updated on " + datetime.datetime.now().strftime("%c"),
                ]
            ),
            dcc.Graph(id="timeline-graph", figure=fig_timeline),
            dcc.Graph(id="bar-chart", figure=fig_bar),
        ]
    )


app.layout = serve_layout


# Flask route for the main page
@server.route("/")
def index():
    return render_template("index.html")


def main():
    app.run_server(host="127.0.0.1", port=8050)


# Run the app
if __name__ == "__main__":
    app.run_server(host="127.0.0.1", port=8050)
