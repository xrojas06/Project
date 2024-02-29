import dash_bootstrap_components as dbc
from dash import html, dcc, Dash, Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash_daq as daq

# Cargar los datos


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
df = pd.read_csv('update_data.csv')
print(df.info())
zonas = df['ZONA_REGION'].unique()
regiones = df['DESC_REGIAO'].unique()
ciudades = df['DESC_CITY'].unique()

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Inicio", href="#")),
        dbc.NavItem(dbc.NavLink("Reporte", href="#")),
        dbc.NavItem(dbc.NavLink("Acerca de", href="#")),
    ],
    brand="Proyecto Customer ID",
    brand_href="#",
    color="dark",
    dark=True,
)

app.layout = dbc.Container([
    navbar,
    html.Br(),
    html.Br(),

    html.H2("REPORTE DE COBERTURA CUSTOMER ID  PARA BDC ", className="text-center"),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cobertura Total de IDs ", className="card-title"),
                    html.H3(id="total-ids", className="card-text")
                ])
            ], color="primary", inverse=True)
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total  ID", className="card-title"),
                    html.H3(id="total-status-id", className="card-text")
                ])
            ], color="success", inverse=True)
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total No ID", className="card-title"),
                    html.H3(id="total-no-id", className="card-text")
                ])
            ], color="danger", inverse=True)
        ], width=6),
    ]),
    html.Br(),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cobertura Total de IDs", className="card-title"),
                    daq.Gauge(
                        id='gauge',
                        color={"gradient":True,"ranges":{"red":[0,10],"yellow":[10,50],"green":[50,100]}},
                        value=2,
                        label='Default',
                        max=100,
                        min=0,
                        showCurrentValue=True,
                        units='%',
                    )
                ]),
                dbc.CardFooter(id="coverage-indicator", style={"color": "black"})
            ], id = 'card-gauge')
        ], width = 3),
        dbc.Col(dcc.Graph(id='grafico-transacciones-con-id-zonal'), width=9),
    ]),html.Br(),


    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-transacciones-con-id-regional')),
    ]),html.Br(),

    # Selector de zona
    dbc.Row([
        dbc.Col(html.Div([
            html.Label("Seleccionar Zona:"),
            dcc.Dropdown(
                id='dropdown-zona',
                options=[{'label': zona, 'value': zona} for zona in zonas],
                multi=False,
                value=zonas[0]  # Seleccionar la primera zona por defecto
            ),
        ])),
        dbc.Col(html.Div([
            html.Label("Seleccionar Región:"),
            dcc.Dropdown(
                id='dropdown-region',
                multi=False,
            ),
        ])),
        dbc.Col(html.Div([
            html.Label("Seleccionar Ciudad:"),
            dcc.Dropdown(
                id='dropdown-ciudad',
                multi=False,
            ),
        ])),
    ]),
    html.Br(),


    # Gráfico de transacciones con ID por tienda
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-transacciones-con-id')),
    ]),
])



@app.callback(
    [Output('gauge', 'value'),
     Output('coverage-indicator', 'className')],
    [Input('dropdown-zona', 'value')]
)
def update_total_coverage(date):
    cobertura_diaria = df['COBERTURA_TOTAL_ID']
    total_coverage = (((cobertura_diaria)).mean())*100
    if total_coverage <= 10:
        indicator_style = {"color": "green"}
    elif total_coverage <= 50:
        indicator_style = {"color": "yellow"}
    else:
        indicator_style = {"color": "red"}

    return (int(float(total_coverage.item()) // 1)), indicator_style

@app.callback(
    Output('dropdown-region', 'options'),
    [Input('dropdown-zona', 'value')]
)
def update_region_options(selected_zona):
    regiones_en_zona = df[df['ZONA_REGION'] == selected_zona]['DESC_REGIAO'].unique()
    return [{'label': region, 'value': region} for region in regiones_en_zona]


@app.callback(
    Output('dropdown-ciudad', 'options'),
    [Input('dropdown-region', 'value')]
)
def update_ciudad_options(selected_region):
    ciudades_en_region = df[df['DESC_REGIAO'] == selected_region]['DESC_CITY'].unique()
    return [{'label': ciudad, 'value': ciudad} for ciudad in ciudades_en_region]


@app.callback(
    Output('grafico-transacciones-con-id', 'figure'),
    [Input('dropdown-zona', 'value'),
     Input('dropdown-region', 'value'),
     Input('dropdown-ciudad', 'value')]
)
def update_transactions_with_id_graph(selected_zona, selected_region, selected_ciudad):
    if selected_ciudad:
        filtered_df = df[df['DESC_CITY'] == selected_ciudad]
    elif selected_region:
        filtered_df = df[df['DESC_REGIAO'] == selected_region]
    elif selected_zona:
        filtered_df = df[df['ZONA_REGION'] == selected_zona]
    else:
        filtered_df = df

    transacciones_por_tienda = filtered_df.groupby('NOME_LOJA')['COBERTURA_ID'].mean()*100
    transacciones_por_tienda = transacciones_por_tienda.reset_index()
    colors = px.colors.qualitative.Plotly
    fig = go.Figure(go.Bar(
        x=transacciones_por_tienda['NOME_LOJA'],
        y=transacciones_por_tienda['COBERTURA_ID'],
        marker_color='royalblue'
    ))

    fig.update_layout(
        title='Cobertura ID',
        xaxis_title='Tienda',
        yaxis_title='Cantidad de Transacciones con ID'
    )

    return fig

@app.callback(
    [Output('grafico-transacciones-con-id-zonal', 'figure')],
    [Input('dropdown-zona', 'value')]
)
def update_transactions_with_id_graph_zonal(date):
    cobertura_por_zona = df.groupby('ZONA_REGION')['COBERTURA_ID'].mean()*100
    cobertura_por_zona = cobertura_por_zona.reset_index()
    colors = px.colors.qualitative.Plotly

    fig = go.Figure(go.Bar(
        x=cobertura_por_zona['ZONA_REGION'],
        y=cobertura_por_zona['COBERTURA_ID'],
        marker_color=colors[:len(cobertura_por_zona)],
    ))

    fig.update_layout(
        title='Cobertura con ID por Zona',
        xaxis_title='Zona',
        yaxis_title='Cobertura ID'
    )

    return [fig]


@app.callback(
    [Output('grafico-transacciones-con-id-regional', 'figure')],
    [Input('dropdown-zona', 'value')]
)
def update_transactions_with_id_graph_zonal(date):
    cobertura_por_zona = df.groupby('DESC_REGIAO')['COBERTURA_ID'].mean()*100
    cobertura_por_zona = cobertura_por_zona.reset_index()

    colors = px.colors.qualitative.Plotly

    fig = go.Figure(go.Bar(
        x=cobertura_por_zona['DESC_REGIAO'],
        y=cobertura_por_zona['COBERTURA_ID'],
        marker_color=colors[:len(cobertura_por_zona)],
    ))

    fig.update_layout(
        title='Cobertura con ID por Región',
        xaxis_title='Región',
        yaxis_title='Cobertura ID'
    )

    return [fig]



@app.callback(
    [Output('total-ids', 'children')],
    [Input('dropdown-zona', 'value')]
)

def total_ids(selected_date):
    total_ids = df['TOTAL_ACUMULADO'].unique()
    return [total_ids]


@app.callback(
    [Output('total-status-id', 'children'),
     Output('total-no-id', 'children')],
    [Input('dropdown-zona', 'value')]
)
def update_totals(selected_date):
    total_status_id = df['TOTAL_ID_ACUMULADO'].unique()
    total_no_id = df['TOTAL_TRANSACCIONES_SIN_CLIENTE'].sum()


    return total_status_id, total_no_id

if __name__ == '__main__':
    app.run_server(debug=True)
