import dash_bootstrap_components as dbc
from dash import html, dcc, Dash, Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash_daq as daq

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Cargar los datos
df = pd.read_csv('update_data.csv')
temp_1 = df.groupby('ID_DIA')[['TOTAL_TRANSACCIONES_CLIENTE_ID', 'TOTAL_TRANSACCIONES_CLIENTE_FE']].sum()
temp_1['Suma_Total'] = temp_1['TOTAL_TRANSACCIONES_CLIENTE_ID'] + temp_1['TOTAL_TRANSACCIONES_CLIENTE_FE']

temp_2 = (df.groupby('ID_DIA')['TOTAL_POS'].sum()).rename('COBERTURA')
cobertura_promedio = (temp_1['Suma_Total'] / temp_2 * 100).reset_index().rename(columns={'0': 'COBERTURA'})


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

    # Filas para los totales de ID
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cobertura Total de IDs hasta la fecha actual", className="card-title"),
                    html.H3(id="total-coverage", className="card-text")
                ])
            ], color="primary", inverse=True)
        ])
    ]),
    html.Br(),


    # Selector de fecha
    dbc.Row([
        dbc.Col(html.Div([
            html.Label("Seleccionar Fecha:   "),
            dcc.DatePickerSingle(
                id='date-picker',
                date=df['ID_DIA'].max(),  # Establecer la fecha predeterminada como la fecha más reciente en los datos
                display_format='DD/MM/YYYY',  # Formato de visualización personalizado para mostrar solo el día, mes y año
            ),
        ])),
    ]),
    html.Br(),
    html.H2("Reporte de Cobertura - Tiendas piloto", className="text-center"),

    # Tabla de datos
    dbc.Row([
        dbc.Col(html.Div(id='table-container')),
    ]),
    html.Br(),

    # Termómetro para los totales de ID

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cobertura Total de IDs hasta la fecha seleccionada", className="card-title"),
                    daq.Gauge(
                        id='gauge',
                        color={"gradient":True,"ranges":{"green":[0,10],"yellow":[10,50],"red":[50,100]}},
                        value=2,
                        label='Default',
                        max=100,
                        min=0,
                        showCurrentValue=True,
                        units='%',
                    )
                ]),
                dbc.CardFooter(id="coverage-indicator", style={"color": "black"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cobertura Diaria", className="card-title"),
                    dcc.Graph(id='grafico-cobertura-diaria')
                ])
            ])
        ], width=9)
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cobertura Diaria por Tienda", className="card-title"),
                    dcc.Graph(id='grafico-cobertura-diaria-tiendas'),
                ])
            ])
        ], width=12)
    ]),
    html.Br(),

    # Layout
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Transacciones por Tienda", className="card-title"),
                    dcc.Graph(id='grafico-transacciones'),
                    html.Div(id='explicacion-grafico-transacciones', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),

                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Porcentaje de Transacciones por Tienda", className="card-title"),
                    dcc.Graph(id='grafico-porcentajes'),
                    html.Div(id='explicacion-grafico-porcentajes', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),

                ])
            ])
        ], width=6)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Tickets con ID por POS y por Tienda", className="card-title"),
                    dcc.Graph(id='grafico-tickets-con-id'),
                    html.Div(id='explicacion-grafico-tickets-con-id', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),

                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Tickets sin ID por POS y por Tienda", className="card-title"),
                    dcc.Graph(id='grafico-tickets-sin-id'),
                    html.Div(id='explicacion-grafico-tickets-sin-id', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
                ])
            ])
        ], width=6)
    ]),html.Br(),
], fluid=True)


# Callback para actualizar el termómetro de la cobertura total de IDs
@app.callback(
    [Output('gauge', 'value'),
     Output('coverage-indicator', 'className')],
    [Input('date-picker', 'date')]
)
def update_total_coverage(selected_date):
    cobertura_diaria = df[['ID_DIA','COBERTURA_DIARIA']]
    total_coverage = ((cobertura_diaria[cobertura_diaria['ID_DIA'] <= selected_date]['COBERTURA_DIARIA'])*100).mean()
    if total_coverage <= 10:
        indicator_style = {"color": "green"}
    elif total_coverage <= 50:
        indicator_style = {"color": "yellow"}
    else:
        indicator_style = {"color": "red"}

    return (int(float(total_coverage.item()) // 1)), indicator_style


# Callback para actualizar la tabla
@app.callback(
    Output('table-container', 'children'),
    [Input('date-picker', 'date')]
)
def update_table(selected_date):
    # Filtrar el DataFrame df por el selected_date
    df_selected = df[df['ID_DIA'] == selected_date]

    # Calcular el total de tickets con ID sumando las columnas TOTAL_TRANSACCIONES_CLIENTE_ID y TOTAL_TRANSACCIONES_CLIENTE_FE
    df_selected['TOTAL_TICKETS_ID'] = df_selected['TOTAL_TRANSACCIONES_CLIENTE_ID'] + df_selected[
        'TOTAL_TRANSACCIONES_CLIENTE_FE']

    # Seleccionar las columnas necesarias para la tabla
    df_selected = df_selected[['ID_DIA', 'NOME_LOJA', 'TOTAL_POS', 'TOTAL_TICKETS_ID', 'COBERTURA_ID']]

    df_selected['ID_DIA'] = pd.to_datetime(df_selected['ID_DIA']).dt.strftime('%Y-%m-%d')
    # Calcular la cobertura promedio para el día seleccionado
    cobertura_promedio_selected = cobertura_promedio[cobertura_promedio['ID_DIA'] == selected_date][0].iloc[0]

    # Convertir la cobertura a porcentaje y agregar el símbolo %
    df_selected['COBERTURA_ID'] = (df_selected['COBERTURA_ID'] * 100).round().astype(int).astype(str) + '%'

    # Calcular la suma total de tickets POS
    total_tickets_sum = df_selected['TOTAL_POS'].sum()

    # Calcular la suma total de tickets con ID
    total_tickets_id_sum = df_selected['TOTAL_TICKETS_ID'].sum()

    # Crear una fila adicional con la cobertura promedio
    df_promedio = pd.DataFrame({'ID_DIA': [pd.to_datetime(selected_date).strftime('%Y-%m-%d')],  # Formatear la fecha para mostrar solo el día
                                'NOME_LOJA': ['Promedio'],
                                'TOTAL_POS': [total_tickets_sum],
                                'TOTAL_TICKETS_ID': [total_tickets_id_sum],
                                'COBERTURA_ID': [str(round(cobertura_promedio_selected)) + '%']})

    # Concatenar la fila promedio al DataFrame seleccionado
    df_selected = pd.concat([df_selected, df_promedio], ignore_index=True)

    # Crear la tabla Dash Bootstrap Components
    table = dbc.Table.from_dataframe(
        df_selected,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )
    return table



@app.callback(
    Output('grafico-cobertura-diaria', 'figure'),
    [Input('date-picker', 'date')]
)
def update_coverage_graph(selected_date):
    fechas = df['ID_DIA'].unique()
    cobertura = df['COBERTURA_DIARIA'].unique()
    cobertura = cobertura*100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fechas, y=cobertura, mode='lines',    fill='toself',
                             fillcolor='rgba(249,112,21,0.2)',line_color='rgb(249,112,21)',text=cobertura,name='Cobertura Diaria'))
    fig.update_layout(title='Cobertura Diaria', xaxis_title='Fecha', yaxis_title='Cobertura')
    return fig


def calcular_porcentajes_por_tienda(selected_date):
        transacciones_por_tienda = df[df['ID_DIA'] == selected_date].groupby('NOME_LOJA')[['TOTAL_TRANSACCIONES_CLIENTE_FE','TOTAL_TRANSACCIONES_CLIENTE_ID','TOTAL_TRANSACCIONES_SIN_CLIENTE','TOTAL_POS']].sum()
        transacciones_por_tienda['TOTAL_SUMA_ID'] = transacciones_por_tienda['TOTAL_TRANSACCIONES_CLIENTE_FE'] + transacciones_por_tienda['TOTAL_TRANSACCIONES_CLIENTE_ID']
        transacciones_por_tienda['PORCENTAJE_CON_ID'] = (transacciones_por_tienda['TOTAL_TRANSACCIONES_CLIENTE_ID'] / (transacciones_por_tienda['TOTAL_POS'])) * 100
        transacciones_por_tienda['PORCENTAJE_SIN_ID'] = (transacciones_por_tienda['TOTAL_TRANSACCIONES_SIN_CLIENTE'] / (transacciones_por_tienda['TOTAL_POS'])) * 100
        return transacciones_por_tienda[['PORCENTAJE_CON_ID', 'PORCENTAJE_SIN_ID']]


@app.callback(
    Output('grafico-porcentajes', 'figure'),
    [Input('date-picker', 'date')]
)
def update_percentage_graph(selected_date):
    porcentajes_por_tienda = calcular_porcentajes_por_tienda(selected_date)
    tiendas = porcentajes_por_tienda.index
    porcentajes_con_id = porcentajes_por_tienda['PORCENTAJE_CON_ID'].values
    porcentajes_sin_id = porcentajes_por_tienda['PORCENTAJE_SIN_ID'].values

    fig = go.Figure(data=[
        go.Bar(name='Con ID', x=tiendas, y=porcentajes_con_id),
        go.Bar(name='Sin ID', x=tiendas, y=porcentajes_sin_id)
    ])

    fig.update_layout(barmode='group', title='Porcentaje de transacciones por tienda', xaxis_title='Tienda', yaxis_title='Porcentaje')

    return fig


def calcular_transacciones_por_tienda(selected_date):
    transacciones_por_tienda = df[df['ID_DIA'] == selected_date].groupby('NOME_LOJA')[['TOTAL_TRANSACCIONES_CLIENTE_FE','TOTAL_TRANSACCIONES_CLIENTE_ID','TOTAL_TRANSACCIONES_SIN_CLIENTE']].sum()
    transacciones_por_tienda['TOTAL_SUMA_ID'] = transacciones_por_tienda['TOTAL_TRANSACCIONES_CLIENTE_FE'] + transacciones_por_tienda['TOTAL_TRANSACCIONES_CLIENTE_ID']

    return transacciones_por_tienda[['TOTAL_SUMA_ID','TOTAL_TRANSACCIONES_SIN_CLIENTE']]

@app.callback(
    Output('grafico-transacciones', 'figure'),
    [Input('date-picker', 'date')]
)
def update_graph(selected_date):
    transacciones_por_tienda = calcular_transacciones_por_tienda(selected_date)
    tiendas = transacciones_por_tienda.index
    transacciones_con_id = transacciones_por_tienda['TOTAL_SUMA_ID'].values
    transacciones_sin_id = transacciones_por_tienda['TOTAL_TRANSACCIONES_SIN_CLIENTE'].values


    fig = go.Figure(data=[
        go.Bar(name='Con ID', x=tiendas, y=transacciones_con_id),
        go.Bar(name='Sin ID', x=tiendas, y=transacciones_sin_id)
    ])

    fig.update_layout(barmode='group', title='Transacciones por tienda', xaxis_title='Tienda', yaxis_title='Cantidad de Transacciones')

    return fig


def obtener_datos_tickets_con_id(selected_date):
    temp = 'TOTAL_TRANSACCIONES_CLIENTE_FE'
    temp_2 = 'TOTAL_TRANSACCIONES_CLIENTE_ID'
    L = []
    for i in range(1,6):
        L.extend([f'{temp}_00{i}', f'{temp_2}_00{i}'])

    transacciones_por_tienda = df[df['ID_DIA'] == selected_date].groupby('NOME_LOJA')[L].sum()
    for i in range(1,6):
        transacciones_por_tienda[f'TOTAL_SUMA_ID_00{i}'] = transacciones_por_tienda[f'TOTAL_TRANSACCIONES_CLIENTE_FE_00{i}'] + transacciones_por_tienda[f'TOTAL_TRANSACCIONES_CLIENTE_ID_00{i}']

    return transacciones_por_tienda

@app.callback(
    Output('grafico-tickets-con-id', 'figure'),
    [Input('date-picker', 'date')]
)
def update_tickets_with_id_graph(selected_date):
    tickets_con_id = obtener_datos_tickets_con_id(selected_date)
    fig = go.Figure()
    for pos in range(1, 6):  # Suponiendo que tienes 5 POS
        pos_data = tickets_con_id[[f'TOTAL_TRANSACCIONES_CLIENTE_ID_00{pos}', f'TOTAL_TRANSACCIONES_CLIENTE_FE_00{pos}']]
        fig.add_trace(go.Bar(x=tickets_con_id.index, y=pos_data.sum(axis=1), name=f'POS {pos}'))
    fig.update_layout(barmode='stack', title='Tickets con ID por POS y por Tienda', xaxis_title='Tienda', yaxis_title='Cantidad de Tickets')
    return fig

def obtener_datos_tickets_sin_id(selected_date):
    temp = 'TOTAL_TRANSACCIONES_SIN_CLIENTE'
    L = [f'{temp}_00{i}' for i in range(1, 6)]

    tickets_sin_id_por_tienda = df[df['ID_DIA'] == selected_date].groupby('NOME_LOJA')[L].sum()
    return tickets_sin_id_por_tienda

@app.callback(
    Output('grafico-tickets-sin-id', 'figure'),
    [Input('date-picker', 'date')]
)
def update_tickets_without_id_graph(selected_date):
    tickets_sin_id = obtener_datos_tickets_sin_id(selected_date)
    fig = go.Figure()
    for pos in range(1, 6):  # Suponiendo que tienes 5 POS
        pos_data = tickets_sin_id[f'TOTAL_TRANSACCIONES_SIN_CLIENTE_00{pos}']
        fig.add_trace(go.Bar(x=tickets_sin_id.index, y=pos_data, name=f'POS {pos}'))
    fig.update_layout(barmode='stack', title='Tickets sin ID por POS y por Tienda', xaxis_title='Tienda', yaxis_title='Cantidad de Tickets')
    return fig

def obtener_datos_cobertura_diaria_por_tienda():
    # Agrupa por día y tienda, y calcula la cobertura diaria promedio para cada tienda
    cobertura_diaria = df.groupby(['ID_DIA', 'NOME_LOJA'])['COBERTURA_ID'].mean().unstack()
    return cobertura_diaria

@app.callback(
    Output('grafico-cobertura-diaria-tiendas', 'figure'),
    [Input('date-picker', 'date')]
)
def update_coverage_graph_store(selected_date):
    cobertura_diaria = obtener_datos_cobertura_diaria_por_tienda()
    fig = go.Figure()
    for tienda in cobertura_diaria.columns:
        fig.add_trace(go.Scatter(x=cobertura_diaria.index, y=cobertura_diaria[tienda]*100, mode='lines+markers', name=tienda,
                                 text=cobertura_diaria[tienda].round(2), textposition='top center'))
    fig.update_layout(title='Cobertura Diaria por Tienda', xaxis_title='Fecha', yaxis_title='Cobertura')
    return fig

def obtener_explicacion_grafica(id_grafica, selected_date):
    # Aquí puedes poner la lógica para obtener el texto de explicación según el ID de la gráfica y la fecha seleccionada
    if id_grafica == 'grafico-transacciones' and selected_date == '2024-02-08':
        return (
                "Promedio de 27% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el "
                + "08/02/2024." +
                " Por otro lado, hubo una disminución de 15 p.p. en el promedio de efectividad." +
                " Y finalmente disminuyo 48 p.p. el promedio de cobertura para Bogotá - La Mariposa."
        )
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-08':
        return f"De las tiendas piloto, Bogotá Chico Norte registró el mayor porcentaje de tickets con Customer ID con un 53% de cobertura promedio efectiva"
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-08':
        return f"Cúcuta no registró tickets con Customer ID en el POS 1."
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-08':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 1.'



    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-07':
        return "Promedio de 42% de efectividad de la cobertura en la solicitud de Customer ID en las tiendas piloto para el 7 de febrero 2024. Además hubo un aumento de 17 p.p. en el promedio de la efectividad de la cobertura."
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-07':
        return "De las tiendas piloto, Bogotá – La Mariposa registró el mayor porcentaje de tickets con Customer ID con un 71% de cobertura promedio efectiva."
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-07':
        return f"Cúcuta no registró tickets con Customer ID en el POS 1."
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-07':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 1.'


    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-06':
        return "Promedio de 25% de efectividad de la cobertura en la solicitud de Customer ID en las tiendas piloto para el 06 de febrero 2024."
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-06':
        return f"De las tiendas piloto, Bogotá – La Mariposa registró el mayor porcentaje de tickets con Customer ID con un 43% de cobertura promedio efectiva."
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-06':
        return f"Bogotá Chico Norte no registró tickets con Customer ID en el POS 1. Y Cúcuta no registró tickets con Customer ID en el POS 3."
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-06':
        return 'Bogotá Chico Norte no registró tickets sin Customer ID en el POS 1. Y Cúcuta no registró tickets sin Customer ID en el POS 3.'



    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-09':
        return "Promedio de 41% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 9 de febrero de 2024, junto con un aumento de 15 p.p. en el promedio de efectividad. También se incrementó 36 p.p. en el promedio de cobertura para Bogotá - La Mariposa y 30 p.p. para Soacha Centro"
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-09':
        return "De las tiendas piloto, Soacha Centro registró el mayor porcentaje de tickets con Customer ID con un 65% de cobertura promedio efectiva."
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-09':
        return f"Neiva no registró tickets con Customer ID en el POS 3, al igual que Soacha no registró en el POS 2."
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-09':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 1.'



    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-10':
        return 'Promedio de 36% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 10 de febrero de 2024. Se presentó una disminución de 5 p.p. en el promedio de efectividad. Sin embargo, Bogotá Chico Norte Tres subió 31 p.p. el promedio de cobertura'
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-10':
        return 'De las tiendas piloto, Bogotá Chico Norte registró el mayor porcentaje de tickets con Customer ID con un 75% de cobertura promedio efectiva.'
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-10':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3, al igual que Soacha no registró tickets con Customer ID en el POS 2.'
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-10':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3, de la misma forma que Soacha no registró tickets sin Customer ID en el POS 2.'


    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-11':
        return 'Promedio de 32% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 11 de febrero de 2024, junto con una disminución de 4 p.p. en el promedio de efectividad.'
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-11':
        return 'De las tiendas piloto, Bogotá Chico Norte registró el mayor porcentaje de tickets con Customer ID con un 65% de cobertura promedio efectiva.'
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-11':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3.'
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-11':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3.'



    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-12':
        return 'Promedio de 35% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 12 de febrero de 2024, junto con un aumento de 3 p.p. en el promedio de efectividad. Además, hubo un incremento 25 p.p. en el promedio de cobertura para Soacha Centro'
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-12':
        return 'De las tiendas piloto, Soacha Centro registró el mayor porcentaje de tickets con Customer ID con un 66% de cobertura promedio efectiva'
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-12':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3; de igual manera que Soacha en el POS 2.'
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-12':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3; de igual manera que Soacha en el POS 2.'


    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-13':
        return 'Promedio de 61% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 13 de febrero de 2024, se presentó un aumento de 27 p.p. en el promedio de efectividad. Finalmente, hubo un incremento 56 p.p. en el promedio de cobertura para Cúcuta Avenida 5'
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-13':
        return 'De las tiendas piloto, Soacha Centro registró el mayor porcentaje de tickets con Customer ID con un 78% de cobertura promedio efectiva'
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-13':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3.'
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-13':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3'



    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-14':
        return 'Promedio de 60% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 14 de febrero de 2024, se presentó una disminución de 1 p.p. en el promedio de efectividad. Finalmente, hubo un incremento de 31 p.p. en el promedio de cobertura para Cúcuta Avenida 5.'
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-14':
        return 'De las tiendas piloto, Cúcuta registró el mayor porcentaje de tickets con Customer ID con un 88% de cobertura promedio efectiva.'
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-14':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3.'
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-14':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3'





    elif id_grafica == 'grafico-transacciones' and selected_date == '2024-02-15':
        return 'Promedio de 74% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 15 de febrero de 2024, se presentó un aumento de 14 p.p. en el promedio de efectividad. Finalmente, hubo un incremento de 36 p.p. en el promedio de cobertura para Bogotá Chico Norte Tres.'
    elif id_grafica == 'grafico-porcentajes' and selected_date == '2024-02-15':
        return 'De las tiendas piloto, Cúcuta Avenida 5 registró el mayor porcentaje de tickets con Customer ID con un 92% de cobertura promedio efectiva.'
    elif id_grafica == 'grafico-tickets-con-id' and selected_date == '2024-02-15':
        return 'Soacha Centro no registró tickets con Customer ID en el POS 3.'
    elif id_grafica == 'grafico-tickets-sin-id' and selected_date == '2024-02-15':
        return 'Todas las tiendas registraron tickets sin Customer ID en cada uno de los POS.'





@app.callback(
    Output('explicacion-grafico-transacciones', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart(selected_date):
    return obtener_explicacion_grafica('grafico-transacciones', selected_date)

@app.callback(
    Output('explicacion-grafico-porcentajes', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_2(selected_date):
    return obtener_explicacion_grafica('grafico-porcentajes', selected_date)

@app.callback(
    Output('explicacion-grafico-tickets-con-id', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_3(selected_date):
    return obtener_explicacion_grafica('grafico-tickets-con-id', selected_date)
@app.callback(
    Output('explicacion-grafico-tickets-sin-id', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_4(selected_date):
    return obtener_explicacion_grafica('grafico-tickets-sin-id', selected_date)

if __name__ == '__main__':
    app.run_server(debug=True)

