import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

TODAY = pd.Timestamp.now()


def parse_source(raw_info):
    info_text = "" if pd.isna(raw_info) else str(raw_info).strip()
    if not info_text:
        return "", ""

    parts = info_text.split("|", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return parts[0].strip(), ""


def extract_bullets(row, limit=None):
    bullets = []
    for key in ["bullet_1", "bullet_2", "bullet_3", "bullet_4", "bullet_5"]:
        value = row.get(key)
        if pd.notna(value) and str(value).strip():
            bullets.append(str(value).strip())

    return bullets if limit is None else bullets[:limit]


def build_info_block(raw_info):
    label, link = parse_source(raw_info)
    if not label:
        return html.P("No external reference for this entry.", className="inspector-info")
    if link:
        return html.A(
            label,
            href=link,
            target="_blank",
            rel="noopener noreferrer",
            className="inline-link",
        )
    return html.P(label, className="inspector-info")


def event_status(row):
    if row["start"] > TODAY:
        return "future"
    if pd.isna(row["end"]) or row["end"] >= TODAY:
        return "present"
    return "past"


def display_end(row):
    if pd.notna(row["end"]):
        return row["end"]

    if row["start"] > TODAY:
        return row["start"] + pd.Timedelta(days=60)
    return TODAY


def row_from_point(point, table):
    selected_title = point.get("customdata", [None])[0]
    if selected_title:
        by_title = table[table["title"] == selected_title]
        if not by_title.empty:
            return by_title.iloc[0]

    y_track = point.get("y")
    scoped = table[table["track_label"] == y_track]
    if scoped.empty:
        return None

    x_val = pd.to_datetime(point.get("x")) if point.get("x") else None
    base_val = pd.to_datetime(point.get("base")) if point.get("base") else None

    if x_val is not None and base_val is not None:
        scoped = scoped[
            (scoped["start"] <= x_val)
            & (scoped["display_end"] >= x_val)
            & (scoped["start"] <= base_val)
            & (scoped["display_end"] >= base_val)
        ]

    if scoped.empty:
        return None
    return scoped.iloc[0]


def selected_work_cards(table):
    priorities = [
        "Dyson - Senior Data Analyst",
        "Fantasy Six Nations Dashboard",
        "Scott Tomlins Portfolio Dashboard (this site)",
    ]
    selected_rows = []
    used_titles = set()

    for title in priorities:
        match = table[table["title"] == title]
        if not match.empty:
            row = match.sort_values("start", ascending=False).iloc[0]
            selected_rows.append(row)
            used_titles.add(row["title"])

    if len(selected_rows) < 3:
        fallback = table[table["type"].isin(["experience", "projects"])].sort_values("start", ascending=False)
        for _, row in fallback.iterrows():
            if row["title"] in used_titles:
                continue
            selected_rows.append(row)
            used_titles.add(row["title"])
            if len(selected_rows) >= 3:
                break

    cards = []
    for row in selected_rows[:3]:
        source_label, source_link = parse_source(row["info"])
        bullets = extract_bullets(row, limit=2)
        summary = bullets[0] if bullets else "Project summary available on request."
        period_end = "Present" if pd.isna(row["end"]) or row["end"] >= TODAY else row["end"].strftime("%Y")
        period_label = f"{row['start'].strftime('%Y')} - {period_end}"

        link_node = None
        if source_label and source_link:
            link_node = html.A(
                source_label,
                href=source_link,
                target="_blank",
                rel="noopener noreferrer",
                className="inline-link project-link",
            )
        elif source_label:
            link_node = html.P(source_label, className="project-meta")

        card_children = [
            html.P(period_label, className="project-meta"),
            html.H3(row["title"], className="project-title"),
            html.P(summary, className="project-copy"),
        ]

        if link_node:
            card_children.append(link_node)

        cards.append(html.Article(className="project-item", children=card_children))

    if not cards:
        cards.append(
            html.Article(
                className="project-item",
                children=[html.P("Selected work entries will appear here.", className="project-copy")],
            )
        )

    return cards


df = pd.read_csv("assets/timeline.csv", parse_dates=["start", "end"], dayfirst=True)
df = df.sort_values(["start", "type", "title"]).reset_index(drop=True)
df["status"] = df.apply(event_status, axis=1)
df["display_end"] = df.apply(display_end, axis=1)
df["track_label"] = df["type"].str.upper()

track_order = [
    track
    for track in ["EXPERIENCE", "EDUCATION", "VOLUNTEERING", "PROJECTS"]
    if track in set(df["track_label"].tolist())
]
if not track_order:
    track_order = sorted(df["track_label"].dropna().unique().tolist())

fig = px.timeline(
    df,
    x_start="start",
    x_end="display_end",
    y="track_label",
    color="status",
    custom_data=["title"],
    category_orders={"track_label": track_order},
    color_discrete_map={
        "past": "#4f5d6b",
        "present": "#45d9e7",
        "future": "#7a8794",
    },
    height=530,
)

fig.update_yaxes(autorange="reversed", title=None, showticklabels=False, showgrid=False)
fig.update_xaxes(
    title=None,
    tickformat="%Y",
    dtick="M12",
    tickfont={"size": 11, "color": "#8f9ba8"},
    showgrid=True,
    gridcolor="#1f2730",
    zeroline=False,
)
fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><extra></extra>")
fig.update_layout(
    showlegend=False,
    bargap=0.62,
    margin={"l": 20, "r": 20, "t": 22, "b": 24},
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"family": "Inter, sans-serif", "color": "#d8dde3"},
)

for trace in fig.data:
    if trace.name == "future":
        trace.opacity = 0.45

for track in track_order:
    fig.add_annotation(
        x=df["start"].min(),
        y=track,
        text=track,
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        yshift=16,
        font={"family": "IBM Plex Mono, monospace", "size": 10, "color": "#8f9ba8"},
    )

present_rows = df[df["status"] == "present"].sort_values("start", ascending=False)
if not present_rows.empty:
    default_row = present_rows.iloc[0]
else:
    default_row = df.sort_values("display_end", ascending=False).iloc[0]

default_title = default_row["title"]
default_info = build_info_block(default_row["info"])
default_bullets = extract_bullets(default_row)

if not default_bullets:
    default_bullets = ["No additional highlights recorded for this entry."]

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Scott Tomlins"
server = app.server

app.layout = html.Div(
    className="page",
    children=[
        html.Main(
            className="exhibit",
            children=[
                html.Section(
                    className="chapter intro",
                    children=[
                        html.P("Personal Data Artefact", className="eyebrow"),
                        html.H1("Scott Tomlins"),
                        html.P("Senior Data Analyst | Bristol, UK", className="role"),
                        html.P(
                            [
                                "Analytical problem-solver with a background in data, engineering, and product delivery. I specialise in reliable product telemetry, practical analytics, and decisions teams can trust.",
                            ],
                            className="lead",
                        ),
                        html.P(
                            [
                                "Find me on ",
                                html.A(
                                    "LinkedIn",
                                    href="https://www.linkedin.com/in/scotttomlins/",
                                    target="_blank",
                                    rel="noopener noreferrer",
                                    className="inline-link",
                                ),
                                ", ",
                                html.A(
                                    "Github",
                                    href="https://github.com/satomlins/",
                                    target="_blank",
                                    rel="noopener noreferrer",
                                    className="inline-link",
                                ),
                                ", ",
                                html.A(
                                    "Medium",
                                    href="https://stomlins.medium.com/",
                                    target="_blank",
                                    rel="noopener noreferrer",
                                    className="inline-link",
                                ),
                                ", or ",
                                html.A(
                                    "email me",
                                    href="mailto:scott@stomlins.com",
                                    target="_blank",
                                    rel="noopener noreferrer",
                                    className="inline-link",
                                ),
                                ".",
                            ],
                            className="contact-links",
                        ),
                    ],
                ),
                html.Section(
                    className="chapter themes",
                    children=[
                        html.Div(
                            className="chapter-head",
                            children=[
                                html.H2("What I Work On"),
                                html.P(
                                    "Themes drawn directly from recent work across Dyson Audio, transformation delivery, and connected product analytics.",
                                    className="chapter-copy",
                                ),
                            ],
                        ),
                        html.Ul(
                            className="focus-list",
                            children=[
                                html.Li(
                                    "Product data reliability: trusted telemetry and semantic-layer metrics that align teams."
                                ),
                                html.Li(
                                    "Decision-focused analytics: measuring feature outcomes and turning usage data into practical actions."
                                ),
                                html.Li(
                                    "Cross-functional delivery: shipping outcomes across engineering, operations, and leadership contexts."
                                ),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="chapter timeline-chapter",
                    children=[
                        html.Div(
                            className="chapter-head",
                            children=[
                                html.H2("Timeline"),
                                html.P(
                                    "Curated chronology of education, product analytics roles, transformation delivery, volunteering, and writing.",
                                    className="chapter-copy",
                                ),
                            ],
                        ),
                        html.Div(
                            className="timeline-layout",
                            children=[
                                html.Div(
                                    className="timeline-canvas",
                                    children=[
                                        dcc.Graph(
                                            id="main_graph",
                                            figure=fig,
                                            config={"displayModeBar": False, "responsive": True},
                                        )
                                    ],
                                ),
                                html.Aside(
                                    className="timeline-notes",
                                    children=[
                                        html.P("Current Focus", className="note-label"),
                                        html.H3(id="title", className="inspector-title", children=default_title),
                                        html.Div(id="info", children=default_info),
                                        html.Ul(
                                            id="bullets",
                                            className="bullet-list",
                                            children=[html.Li(text) for text in default_bullets],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="chapter selected-work",
                    children=[
                        html.Div(
                            className="chapter-head",
                            children=[
                                html.H2("Projects"),
                                html.P(
                                    "A short set of completed projects and deliverables.",
                                    className="chapter-copy",
                                ),
                            ],
                        ),
                        html.Div(className="project-list", children=selected_work_cards(df)),
                    ],
                ),
            ],
        )
    ],
)


@app.callback(
    Output("title", "children"),
    Output("info", "children"),
    Output("bullets", "children"),
    Input("main_graph", "hoverData"),
    Input("main_graph", "clickData"),
)
def update_info(hover_data, click_data):
    payload = click_data or hover_data
    if not payload or "points" not in payload or not payload["points"]:
        return default_title, default_info, [html.Li(text) for text in default_bullets]

    selected = row_from_point(payload["points"][0], df)
    if selected is None:
        return default_title, default_info, [html.Li(text) for text in default_bullets]

    bullet_text = extract_bullets(selected)
    if not bullet_text:
        bullet_text = ["No additional highlights recorded for this entry."]

    return selected["title"], build_info_block(selected["info"]), [html.Li(text) for text in bullet_text]


if __name__ == "__main__":
    app.run_server(debug=True)
