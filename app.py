# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_iconify import DashIconify
import plotly.express as px

icon_size = 20
icon_style = {'margin': '0.1rem 0.4rem 0'}

today = pd.today = pd.Timestamp.now()
bd = pd.Timestamp('00:00:00 2000-04-08')
agey = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
# aged = (today - pd.Timedelta('{}y'.format(agey)) - bd).days

about_me = "Hi, I'm Scott! I'm a {} year old Data Scientist based in Bristol" \
           " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et" \
           " dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip" \
           " ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu" \
           " fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt" \
           " mollit anim id est laborum." \
    .format(agey)

df = pd.read_csv('assets/timeline.csv', parse_dates=['start', 'end'], dayfirst=True)
df['end'] = df['end'].apply(
    lambda x: x if (x > pd.Timestamp('00:00:00 2000-01-01')) & (x < pd.Timestamp.now()) else pd.Timestamp.now())
prevClickData = None

fig = px.timeline(df,
                  x_start="start",
                  x_end="end",
                  y="type",
                  color='title',
                  template='plotly_dark',
                  labels={'type': ''},
                  height=400,
                  title='Hover/click on the plot for more information'
                  )

fig.update_traces(
    hovertemplate='%{y}',
)

fig.update_layout(showlegend=False,
                  yaxis={'type': 'category', 'visible': True, 'tickangle': -45},
                  margin=dict(l=0, r=0, t=80, b=40),
                  font_family='Montserrat, Roboto Mono'
                  )

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}], )

app.title = 'stomlins'

server = app.server

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
                                    'margin': '0 0 0 0',
                                    'color': '#00FFFF',
                                },
                                className='container'
                            ),
                            html.H2(
                                'Data Scientist - Bristol UK',
                                style={
                                    "textAlign": "center",
                                    'margin': '0 0 0 0',
                                },
                                className='container',
                            )
                        ],
                        style={'margin': '2em 0 0'},
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
                            src="assets/PP.jpeg",
                            className='twelve columns img',
                            # style={'height': '20em', 'width': 'auto'}
                        ),
                    ], className='container img_container',  # , className='two columns',
                        # style={'display': 'inline-block', 'border-style': 'solid', 'position': 'static',
                        #        'max-height': '100%', 'float': 'left'}
                    ),
                    html.Div([
                        html.P(
                            about_me,
                            style={'font-size': '1.2em',
                                   'text-align': 'justify',
                                   'text-justify': 'inter-word',
                                   'top': '50%',
                                   'margin': '0 0 0 0',
                                   },
                            className='twelve columns',
                        )
                    ],
                        className='container offset-by-half column',
                        style={'flex': '1'},
                        # style={'display': 'inline-block', 'border-style': 'solid'}
                        # className='nineplus columns container offset-by-half column',
                    )
                ],
                id="main_text",
                className="row",
                style={'margin': '2em 0 0'},
            ),
            html.Hr(),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id='main_graph',
                                      figure=fig,
                                      )
                        ],
                        className='plot eight columns',
                    ),
                    html.Div(
                        [
                            html.H5(
                                id="title",
                                className="info_text"
                            ),
                            html.Div(
                                # html.H6(
                                #     'Hover/click on the plot for more information',
                                #     className="info_text"
                                # ),
                                id='info'),
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
                        className='container four columns',
                    ),
                ],
                className='row',
            ),
        ],
        id="mainContainer",
        className='main_container'
    ),
    html.Div([
        html.Div([
            dcc.Link(
                DashIconify(
                    icon="bi:envelope",
                    width=icon_size,
                    height=icon_size,
                    style=icon_style
                ),
                target='_blank',
                href='mailto:scott@stomlins.com',
            ),
            dcc.Link(
                DashIconify(
                    icon="bi:linkedin",
                    width=icon_size,
                    height=icon_size,
                    style=icon_style
                ),
                target='_blank',
                href='https://www.linkedin.com/in/scotttomlins/',
            ),
            dcc.Link(
                DashIconify(
                    icon="bi:github",
                    width=icon_size,
                    height=icon_size,
                    style=icon_style
                ),
                target='_blank',
                href='https://github.com/satomlins/',
            ),
            dcc.Link(
                DashIconify(
                    icon="bi:medium",
                    width=icon_size,
                    height=icon_size,
                    style=icon_style
                ),
                target='_blank',
                href='https://stomlins.medium.com/',
            ),
        ]),
        html.P('© {} Scott Tomlins   |   website by Scott Tomlins'.format(pd.Timestamp.now().year)),
    ],
        className='footer')
],
)


def prettify_row(row):
    return 0


@app.callback(Output('title', 'children'),
              Output('info', 'children'),
              Output('bullets', 'children'),
              [Input('main_graph', 'hoverData'),
               Input('main_graph', 'clickData')])
def update_info(hoverData, clickData):
    global df
    global prevClickData
    global newData

    if clickData == prevClickData:
        newData = hoverData
    else:
        newData = clickData

    x = newData['points'][0]['x']
    x2 = newData['points'][0]['base']
    y = newData['points'][0]['y']

    row = df[(df['start'] <= x)
             & (df['end'] >= x)
             & (df['start'] <= x2)
             & (df['end'] >= x2)
             & (df['type'] == y)]

    prevClickData = clickData

    linkInfo = row['info'].values[0].split('|')

    if len(linkInfo) == 1:
        info = html.H6(
            row['info'],
            className="info_text"
        )
    else:
        info = dcc.Link(
            html.H6(
                linkInfo[0],
                className="info_text"
            ),
            target='_blank',
            href=linkInfo[1],
        ),

    print(info)

    return row['title'], \
           info, \
           [html.Li(i) for i in (row['bullet_1'],
                                 row['bullet_2'],
                                 row['bullet_3'],
                                 row['bullet_4'],
                                 row['bullet_5']) if i.any()]


# Main
if __name__ == '__main__':
    app.run_server()  # debug=True, port=8069)
