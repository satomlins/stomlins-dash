# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

today = pd.today = pd.Timestamp.now()
bd = pd.Timestamp('00:00:00 2000-04-08')
agey = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
aged = (today - pd.Timedelta('{}y'.format(agey)) - bd).days

about_me = "Hi, I'm Scott, age {} years and {} days! This is my website." \
           " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et" \
           " dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip" \
           " ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu" \
           " fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt" \
           " mollit anim id est laborum.".format(agey, aged)

df = pd.read_csv('assets/timeline.csv', parse_dates=['start', 'end'], dayfirst=True)
df['end'] = df['end'].apply(
    lambda x: x if (x > pd.Timestamp('00:00:00 2000-01-01')) & (x < pd.Timestamp.now()) else pd.Timestamp.now())
prevClickData = {}

fig = px.timeline(df,
                  x_start="start",
                  x_end="end",
                  y="type",
                  color='title',
                  template='plotly_dark',
                  labels={'type': ''}
                  )

fig.update_traces(
    hovertemplate='%{y}',
)

fig.update_layout(showlegend=False,
                  yaxis={'type': 'category', 'visible': True})

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}], )

app.title = 'stomlins'

server = app.server


# layout = dict(
#     autosize=True,
#     automargin=True,
#     margin=dict(
#         l=30,
#         r=30,
#         b=20,
#         t=40
#     ),
#     hovermode="closest",
#     plot_bgcolor="#F9F9F9",
#     paper_bgcolor="#F9F9F9",
#     legend=dict(font=dict(size=10), orientation='h'),
#     title='Satellite Overview',
#     mapbox=dict(
#         # accesstoken=mapbox_access_token,
#         style="light",
#         center=dict(
#             lon=-78.05,
#             lat=42.54
#         ),
#         zoom=7,
#     )
# )

# Create app layout
app.layout = html.Div([
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                'Scott Tomlins',
                                style={
                                    "textAlign": "center",
                                },
                            ),
                            html.H3(
                                'Data Scientist - Bristol, UK',
                                style={
                                    "textAlign": "center",
                                },
                            )
                        ],
                        className='twelve columns'
                    ),
                ],
                id="header",
                className='row',
            ),

            html.Div(
                [
                    html.Div([
                        html.Img(
                            src="assets/PP_circ.png",
                            className='twelve columns'
                        ),
                    ], className='three columns pretty_container',
                    ),
                    html.Div([
                        html.P(
                            about_me,
                            style={'font-size': '1.4em',
                                   'text-align': 'justify',
                                   'text-justify': 'inter-word',
                                   'top': '50%',
                                   'margin': 0,
                                   'position': 'absolute',
                                   'transform': 'translate(0, -50%)'
                                   }
                        )
                    ], className='nine columns pretty_container',
                    )
                ],
                id="main_text",
                className="pretty_container row"

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
                                'Hover over the timeline for information',
                                id="info",
                                className="info_text"
                            ),
                            html.Div(
                                [
                                    html.Ul(id="bullets",
                                            style={'list-style-position': 'outside',
                                                   'list-style-type': 'disc',
                                                   'margin': '1em'}
                                            )
                                ],
                                className="info_text"
                            ),
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
        },
        className='main_container'
    ),
    html.Div([html.P('© {} Scott Tomlins   |   website by Scott Tomlins'.format(pd.Timestamp.now().year))],
             className='footer')
]
)


def prettify_row(row):
    return 0


@app.callback(Output('title', 'children'),
              Output('info', 'children'),
              Output('bullets', 'children'),
              [Input('main_graph', 'hoverData'),
               Input('main_graph', 'clickData')])
def make_main_figure(hoverData, clickData):
    global df
    global prevClickData

    print('click', clickData)
    print('hover', hoverData)

    if clickData == prevClickData:
        newData = hoverData
    else:
        newData = clickData

    x = hoverData['points'][0]['x']
    x2 = hoverData['points'][0]['base']
    y = hoverData['points'][0]['y']

    row = df[(df['start'] <= x)
             & (df['end'] >= x)
             & (df['start'] <= x2)
             & (df['end'] >= x2)
             & (df['type'] == y)]

    prevClickData = clickData
    # prevHoverData = hoverData

    return row['title'], \
           row['info'], \
           [html.Li(i) for i in (row['bullet_1'],
                                 row['bullet_2'],
                                 row['bullet_3'],
                                 row['bullet_4'],
                                 row['bullet_5']) if i.any()]


# Main
if __name__ == '__main__':
    # app.server.run(debug=True)
    app.run_server()  # debug=True, port=8069)
