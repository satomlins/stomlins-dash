# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

df = pd.read_csv('assets/timeline.csv', parse_dates=['start', 'end'], dayfirst=True)
df['end'] = df['end'].apply(
    lambda x: x if (x > pd.Timestamp('00:00:00 2000-01-01')) & (x < pd.Timestamp.now()) else pd.Timestamp.now())

fig = px.timeline(df, x_start="start",
                  x_end="end",
                  y="type",
                  color='title',
                  )

fig.update_traces(
    hovertemplate='%{y}',
    # hoverinfo = 'skip'
)

fig.update_layout(showlegend=False)

fig.update_yaxes(type='category')

app = dash.Dash(__name__)
server=app.server

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Satellite Overview',
    mapbox=dict(
        # accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-78.05,
            lat=42.54
        ),
        zoom=7,
    )
)

# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src="assets/PP_circ.png",
                    className='two columns',
                ),
                html.Div(
                    [
                        html.H1(
                            'Scott Tomlins',

                        ),
                        html.H3(
                            'Data Scientist - Bristol, UK',
                        )
                    ],

                    className='ten columns'
                ),

            ],
            id="header",
            className='row',
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'Filter by construction date (or select range in histogram):',
                            className="control_label"
                        ),
                        dcc.RangeSlider(
                            id='year_slider',
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className="dcc_control"
                        ),
                        html.P(
                            'Filter by well status:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='well_status_selector',
                            options=[
                                {'label': 'All ', 'value': 'all'},
                                {'label': 'Active only ', 'value': 'active'},
                                {'label': 'Customize ', 'value': 'custom'}
                            ],
                            value='active',
                            labelStyle={'display': 'inline-block'},
                            className="dcc_control"
                        ),
                        html.P(
                            'Filter by well type:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='well_type_selector',
                            options=[
                                {'label': 'All ', 'value': 'all'},
                                {'label': 'Productive only ',
                                 'value': 'productive'},
                                {'label': 'Customize ', 'value': 'custom'}
                            ],
                            value='productive',
                            labelStyle={'display': 'inline-block'},
                            className="dcc_control"
                        ),
                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("I can put some info in here")
                                    ],
                                    id="box1",
                                    className="pretty_container four columns"
                                ),
                                html.Div(
                                    [
                                        html.P("I can put some info in here")
                                    ],
                                    id="box2",
                                    className="pretty_container four columns"
                                ),
                                html.Div(
                                    [
                                        html.P("I can put some info in here")
                                    ],
                                    id="box3",
                                    className="pretty_container four columns"
                                ),

                            ],
                            id="infoContainer",
                            className="row"
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id='count_graph',
                                )
                            ],
                            id="countGraphContainer",
                            className="pretty_container"
                        )
                    ],
                    id="rightCol",
                    className="eight columns"
                )
            ],
            className="row"
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main_graph',
                                  figure=fig,
                                  )
                    ],
                    className='pretty_container eight columns',
                ),
                html.Div(
                    [
                        html.H5(
                            id="title",
                            className="info_text"
                        ),
                        html.H6(
                            id="info",
                            className="info_text"
                        ),
                        html.Div(
                            id="bullets",
                            className="info_text"
                        ),

                    ],
                    className='pretty_container four columns',
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='pie_graph')
                    ],
                    className='pretty_container eight columns',
                ),
                html.Div(
                    [
                        dcc.Graph(id='aggregate_graph')
                    ],
                    className='pretty_container four columns',
                ),
            ],
            className='row'
        ),
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


def prettify_row(row):
    return 0


@app.callback(Output('title', 'children'),
              Output('info', 'children'),
              Output('bullets', 'children'),
              [Input('main_graph', 'hoverData')])
# [Input('well_statuses', 'value'),
#  Input('well_types', 'value'),
#  Input('year_slider', 'value')],
# [State('lock_selector', 'values'),
#  State('main_graph', 'relayoutData')])
def make_main_figure(hoverData):
    global df

    x = hoverData['points'][0]['x']
    x2 = hoverData['points'][0]['base']
    y = hoverData['points'][0]['y']

    print(hoverData)

    row = df[(df['start'] <= x)
             & (df['end'] >= x)
             & (df['start'] <= x2)
             & (df['end'] >= x2)
             & (df['type'] == y)]

    print(row)

    return row['title'], row['info'], row['bullet_1']


# Main
if __name__ == '__main__':
    # app.server.run(debug=True)
    app.run_server() #debug=True, port=8069)
