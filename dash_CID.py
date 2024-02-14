import dash_bootstrap_components as dbc
from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash_leaflet as dl
import geopandas as gpd
import folium

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Cargar los datos
df = pd.read_csv('update_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
# Calcular cobertura por fecha
cobertura_por_fecha = (
    df
    .assign(Status_ID=df['Status'] == 'ID')
    .groupby(['Date', 'Desc. Store'])
    .agg(
        Total_Tickets=('Transaction Id.', 'nunique'),
        Tickets_with_ID=('Status_ID', 'sum')
    )
    .reset_index()
)

cobertura_por_fecha['Coverage'] = cobertura_por_fecha['Tickets_with_ID'] / cobertura_por_fecha['Total_Tickets'] * 100
cobertura_promedio = (cobertura_por_fecha.groupby('Date')['Tickets_with_ID'].sum()/cobertura_por_fecha.groupby('Date')['Total_Tickets'].sum() * 100).rename('Coverage').reset_index()


nuevo_dataframe = cobertura_por_fecha.reset_index()
nuevo_dataframe.rename(columns={'level_0': 'Date'}, inplace=True)
nuevo_dataframe.drop(columns=['index'], inplace=True)
df_filter = df[['Desc. Store', 'Latitud','Longitud']]
cobertura_por_fecha_1 = nuevo_dataframe[['Date','Desc. Store','Coverage']]
cobertura_fecha_especifica = pd.merge(cobertura_por_fecha_1, df_filter, on='Desc. Store', how='left').drop_duplicates().dropna()






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
def create_bar_chart(selected_date):
    # Filtrar el dataframe por la fecha seleccionada
    df_selected = df[df['Date'] == selected_date]

    # Agrupar los datos por tienda y estado
    grouped_data = df_selected.groupby('Desc. Store')['Status'].value_counts().unstack().fillna(0)

    # Crear la figura de Plotly
    fig = go.Figure(data=[
        go.Bar(name='Invalid ID', x=grouped_data.index, y=grouped_data['Invalid ID'], text=grouped_data['Invalid ID'], textposition='auto', insidetextanchor='end'),
        go.Bar(name='No ID', x=grouped_data.index, y=grouped_data['No ID'], text=grouped_data['No ID'], textposition='auto', insidetextanchor='end'),
        go.Bar(name='ID', x=grouped_data.index, y=grouped_data['ID'], text=grouped_data['ID'], textposition='auto', insidetextanchor='end')
    ])

    fig.update_layout(title='Cantidad de ID',
                      xaxis=dict(title='Tienda'),
                      yaxis=dict(title='Cantidad'))

    return fig

def create_second_bar_chart(selected_date):
    df_selected = df[df['Date'] == selected_date]
    grouped_data = df_selected.groupby('Desc. Store')['Status'].value_counts(normalize=True).unstack() * 100

    # Crear el gráfico de barras
    fig = go.Figure(data=[
        go.Bar(name='Invalid ID', x=grouped_data.index, y=grouped_data['Invalid ID'], text=grouped_data['Invalid ID'].round(1).astype(str) + '%', textposition='auto', insidetextanchor='end'),
        go.Bar(name='No ID', x=grouped_data.index, y=grouped_data['No ID'], text=grouped_data['No ID'].round(1).astype(str) + '%', textposition='auto', insidetextanchor='end'),
        go.Bar(name='ID', x=grouped_data.index, y=grouped_data['ID'], text=grouped_data['ID'].round(1).astype(str) + '%', textposition='auto', insidetextanchor='end')
    ])

    # Agregar título y etiquetas de los ejes
    fig.update_layout(title='Porcentaje ID',
                      xaxis=dict(title='Tienda'),
                      yaxis=dict(title='Porcentaje'))

    # Mostrar el gráfico
    return fig

def create_bar_chart_id_pos(selected_date):
    df_new_date = df[df['Date'] == selected_date]
    filtered_data = df_new_date[(df_new_date['Status'] == 'ID')]
    grouped_data = filtered_data.groupby('Desc. Store')['Id Pos'].value_counts().unstack()

    # Crear el gráfico de barras
    fig = go.Figure(data=[
        go.Bar(name='POS 1', x=grouped_data.index, y=grouped_data[1], text=grouped_data[1], textposition='auto', insidetextanchor='end'),
        go.Bar(name='POS 2', x=grouped_data.index, y=grouped_data[2], text=grouped_data[2], textposition='auto', insidetextanchor='end'),
        go.Bar(name='POS 3', x=grouped_data.index, y=grouped_data[3], text=grouped_data[3], textposition='auto', insidetextanchor='end'),
        go.Bar(name='POS 4', x=grouped_data.index, y=grouped_data[4], text=grouped_data[4], textposition='auto', insidetextanchor='end')
    ])

    # Agregar título y etiquetas de los ejes
    fig.update_layout(title='Cantidad de ID por POS',
                      xaxis=dict(title='Tienda'),
                      yaxis=dict(title='Cantidad'))

    # Mostrar el gráfico
    return fig

def create_bar_chart_noid_pos(selected_date):
    df_new_date = df[df['Date'] == selected_date]
    filtered_data = df_new_date[(df_new_date['Status'] == 'No ID')]
    grouped_data = filtered_data.groupby('Desc. Store')['Id Pos'].value_counts().unstack()

    # Crear el gráfico de barras
    fig = go.Figure(data=[
        go.Bar(name='POS 1', x=grouped_data.index, y=grouped_data[1], text=grouped_data[1], textposition='auto', insidetextanchor='end'),
        go.Bar(name='POS 2', x=grouped_data.index, y=grouped_data[2], text=grouped_data[2], textposition='auto', insidetextanchor='end'),
        go.Bar(name='POS 3', x=grouped_data.index, y=grouped_data[3], text=grouped_data[3], textposition='auto', insidetextanchor='end'),
        go.Bar(name='POS 4', x=grouped_data.index, y=grouped_data[4], text=grouped_data[4], textposition='auto', insidetextanchor='end')
    ])

    # Agregar título y etiquetas de los ejes
    fig.update_layout(title='Cantidad de No ID por POS',
                      xaxis=dict(title='Tienda'),
                      yaxis=dict(title='Cantidad' ))

    # Mostrar el gráfico
    return fig

def create_histogram_length(selected_date):
    df_new_date = df[df['Date'] == selected_date]
    filtered_data = df_new_date[(df_new_date['Status'] == 'ID') | (df_new_date['Status'] == 'Invalid ID')]

    filtered_data['Id Length'] = filtered_data['Id Cliente'].astype(str).apply(len)

    fig = px.histogram(filtered_data, x='Id Length', title='Histograma de longitud de IDs de cliente', color='Id Length')

    fig.update_traces(texttemplate='%{y}', textposition='auto')  # Agrega la cantidad encima de la barra
    fig.update_xaxes(title_text='Longitud del ID', tickvals=list(range(filtered_data['Id Length'].min(), filtered_data['Id Length'].max() + 1))) # Mostrar todos los números en el eje x
    fig.update_yaxes(title_text='Frecuencia')

    return fig


def create_bar_invalid(selected_date):
    df_new_date = df[df['Date'] == selected_date]
    count_by_store = df_new_date.groupby(['Desc. Store', 'Status']).size().reset_index(name='Count')

    invalid_counts = count_by_store[count_by_store['Status'] == 'Invalid ID']
    max_valor = invalid_counts['Count'].max()
    # Visualizar los resultados en una gráfica de barras
    fig = px.bar(invalid_counts, x='Desc. Store', y='Count', color='Desc. Store',
                 title='Cantidad de IDs de Cliente Inválidos por Tienda',
                 labels={'Count': 'Cantidad de IDs de Cliente', 'Desc. Store': 'Tienda', 'Invalid_ID': 'Inválido'})

    fig.update_traces(texttemplate='%{y}', textposition='auto')  # Agrega la cantidad encima de la barra
    return fig

def create_bar_duplicated(selected_date):
    df_new_date = df[df['Date'] == selected_date]
    invalid_ids = df_new_date[(df_new_date['Id Cliente'] < 1000000) | (df_new_date['Id Cliente'] > 10000000000) | (df_new_date['Id Cliente'].isna())]

    duplicados_clean = df_new_date[~df_new_date.index.isin(invalid_ids.index) & df_new_date.duplicated(subset=['Id Cliente'], keep=False)]

    count_duplicates_clean = duplicados_clean.groupby('Desc. Store').size().reset_index(name='Cantidad de Clientes con más de un registro')
    max_valor = count_duplicates_clean['Cantidad de Clientes con más de un registro'].max()
    # Visualizar los resultados en un gráfico de barras
    fig = px.bar(count_duplicates_clean, x='Desc. Store', y='Cantidad de Clientes con más de un registro',
                 title='Cantidad de IDs de Cliente únicos por Tienda',
                 labels={'Cantidad de Duplicados': 'Cantidad de Duplicados', 'Desc. Store': 'Tienda'}, color='Desc. Store')
    fig.update_traces(texttemplate='%{y}', textposition='auto')
    return fig

def obtener_explicacion_grafica(id_grafica, selected_date):
    # Aquí puedes poner la lógica para obtener el texto de explicación según el ID de la gráfica y la fecha seleccionada
    if id_grafica == 'bar-chart' and selected_date == '2024-02-08':
        return (
                "Promedio de 27% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el "
                 + "08/02/2024." +
                " Por otro lado, hubo una disminución de 15 p.p. en el promedio de efectividad." +
                " Y finalmente disminuyo 48 p.p. el promedio de cobertura para Bogotá - La Mariposa."
        )
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-08':
         return f"De las tiendas piloto, Bogotá Chico Norte registró el mayor porcentaje de tickets con Customer ID con un 53% de cobertura promedio efectiva"
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-08':
        return f"Cúcuta no registró tickets con Customer ID en el POS 1."
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-08':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 1.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-08':
        return 'Hay persistencia de ID’s con longitudes atípicas. Siguen catalogándose como posibles errores de digitación'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-08':
        return 'Los datos no válidos del 8 de febrero fueron el 1% del total de los tickets'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-08':
        return 'Las tiendas de Bogotá Chico Norte Tres y Soacha Centro registraron tickets con ID más de una vez. '

    elif id_grafica == 'bar-chart' and selected_date == '2024-02-07':
        return "Promedio de 42% de efectividad de la cobertura en la solicitud de Customer ID en las tiendas piloto para el 7 de febrero 2024. Además hubo un aumento de 17 p.p. en el promedio de la efectividad de la cobertura."
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-07':
        return "De las tiendas piloto, Bogotá – La Mariposa registró el mayor porcentaje de tickets con Customer ID con un 71% de cobertura promedio efectiva."
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-07':
        return f"Cúcuta no registró tickets con Customer ID en el POS 1."
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-07':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 1.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-07':
        return 'El histograma señala la longitud de los ID’s de cliente. Se aprecia una distribución típica de 8 a 12 dígitos, que son consistentes con la cantidad de números en las cédulas o NIT’s. Sin embargo, se nota una proporción de ID’s con cantidades atípicas, lo que sugiere posibles errores de digitación.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-07':
        return 'Los datos no válidos del 07 de febrero fueron el 1.3% del total de los tickets.'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-07':
        return 'El 07 de febrero se detectó una cantidad importante de ID’s con más de un registro en varias tiendas, lo que podría ser un primer indicador de comportamiento de compra o fidelidad de los clientes. '

    elif id_grafica == 'bar-chart' and selected_date == '2024-02-06':
        return "Promedio de 25% de efectividad de la cobertura en la solicitud de Customer ID en las tiendas piloto para el 06 de febrero 2024."
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-06':
        return f"De las tiendas piloto, Bogotá – La Mariposa registró el mayor porcentaje de tickets con Customer ID con un 43% de cobertura promedio efectiva."
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-06':
        return f"Bogotá Chico Norte no registró tickets con Customer ID en el POS 1. Y Cúcuta no registró tickets con Customer ID en el POS 3."
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-06':
        return 'Bogotá Chico Norte no registró tickets sin Customer ID en el POS 1. Y Cúcuta no registró tickets sin Customer ID en el POS 3.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-06':
        return 'El histograma señala la longitud de los ID’s de cliente. Se aprecia una distribución típica de 8 a 12 dígitos, que son consistentes con la cantidad de números en las cédulas o NIT’s. Sin embargo, se nota una proporción de ID’s con cantidades atípicas, lo que sugiere posibles errores de digitación.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-06':
        return 'Los datos no válidos del 06 de febrero fueron el 0.5% del total de los tickets.'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-06':
        return 'El 06 de febrero se detectó ID’s con más de un registro en varias tiendas, lo que podría ser un primer indicio del comportamiento de compra de los clientes. '


    elif id_grafica == 'bar-chart' and selected_date == '2024-02-09':
        return "Promedio de 41% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 9 de febrero de 2024, junto con un aumento de 15 p.p. en el promedio de efectividad. También se incrementó 36 p.p. en el promedio de cobertura para Bogotá - La Mariposa y 30 p.p. para Soacha Centro"
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-09':
        return "De las tiendas piloto, Soacha Centro registró el mayor porcentaje de tickets con Customer ID con un 65% de cobertura promedio efectiva."
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-09':
        return f"Neiva no registró tickets con Customer ID en el POS 3, al igual que Soacha no registró en el POS 2."
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-09':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 1.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-09':
        return 'Hay persistencia de ID’s con longitudes atípicas. Sin embargo, para el 09 de febrero no hay casos de errores con cantidad de dígitos menores 6.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-09':
        return 'Los datos no válidos del 09 de febrero fueron el 1.4% del total de los tickets'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-09':
        return 'El 09 de febrero la tienda de Cúcuta Avenida 5 no registró tickets con ID más de una vez'


    elif id_grafica == 'bar-chart' and selected_date == '2024-02-10':
        return 'Promedio de 36% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 10 de febrero de 2024. Se presentó una disminución de 5 p.p. en el promedio de efectividad. Sin embargo, Bogotá Chico Norte Tres subió 31 p.p. el promedio de cobertura'
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-10':
        return 'De las tiendas piloto, Bogotá Chico Norte registró el mayor porcentaje de tickets con Customer ID con un 75% de cobertura promedio efectiva.'
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-10':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3, al igual que Soacha no registró tickets con Customer ID en el POS 2.'
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-10':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3, de la misma forma que Soacha no registró tickets sin Customer ID en el POS 2.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-10':
        return 'Hay persistencia de ID’s con longitudes atípicas. De nuevo se registran ID’s con cantidad de dígitos menores a 6.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-10':
        return 'Los datos no válidos del 10 de febrero fueron el 3.6% del total de los tickets'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-10':
        return 'El 10 de febrero la tienda de Cúcuta Avenida 5 no registró tickets con ID más de una vez.'

    elif id_grafica == 'bar-chart' and selected_date == '2024-02-11':
        return 'Promedio de 32% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 11 de febrero de 2024, junto con una disminución de 4 p.p. en el promedio de efectividad.'
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-11':
        return 'De las tiendas piloto, Bogotá Chico Norte registró el mayor porcentaje de tickets con Customer ID con un 65% de cobertura promedio efectiva.'
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-11':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3.'
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-11':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-11':
        return 'Hay persistencia de ID’s con longitudes atípicas. De nuevo se registran ID’s con cantidad de dígitos en todas las categorías.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-11':
        return 'Los datos no válidos del 11 de febrero fueron el 1.6% del total de los tickets.'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-11':
        return 'El 11 de febrero la tienda de Cúcuta Avenida 5 no registró tickets con ID más de una vez.'


    elif id_grafica == 'bar-chart' and selected_date == '2024-02-12':
        return 'Promedio de 35% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 12 de febrero de 2024, junto con un aumento de 3 p.p. en el promedio de efectividad. Además, hubo un incremento 25 p.p. en el promedio de cobertura para Soacha Centro'
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-12':
        return 'De las tiendas piloto, Soacha Centro registró el mayor porcentaje de tickets con Customer ID con un 66% de cobertura promedio efectiva'
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-12':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3; de igual manera que Soacha en el POS 2.'
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-12':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3; de igual manera que Soacha en el POS 2.'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-12':
        return 'Hay persistencia de ID’s con longitudes atípicas. Se mantiene la cantidad de dígitos con errores en todas las categorías.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-12':
        return 'Los datos no válidos del 12 de febrero fueron el 5.2% del total de los tickets.'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-12':
        return 'El 12 de febrero la tienda de Cúcuta Avenida 5 no registró tickets con ID más de una vez.'

    elif id_grafica == 'bar-chart' and selected_date == '2024-02-13':
        return 'Promedio de 61% de efectividad de la cobertura en la solicitud de Customer ID para las tiendas piloto el 13 de febrero de 2024, se presentó un aumento de 27 p.p. en el promedio de efectividad. Finalmente, hubo un incremento 56 p.p. en el promedio de cobertura para Cúcuta Avenida 5'
    elif id_grafica == 'bar-chart-2' and selected_date == '2024-02-13':
        return 'De las tiendas piloto, Soacha Centro registró el mayor porcentaje de tickets con Customer ID con un 78% de cobertura promedio efectiva'
    elif id_grafica == 'bar-chart-3' and selected_date == '2024-02-13':
        return 'Cúcuta no registró tickets con Customer ID en el POS 3.'
    elif id_grafica == 'bar-chart-4' and selected_date == '2024-02-13':
        return 'Cúcuta no registró tickets sin Customer ID en el POS 3'
    elif id_grafica == 'bar-chart-5' and selected_date == '2024-02-13':
        return 'Hay persistencia de ID’s con longitudes atípicas. Sin embargo, no hay ID’s con dígitos con cantidad de 1 y 2.'
    elif id_grafica == 'bar-chart-6' and selected_date == '2024-02-13':
        return 'Los datos no válidos del 13 de febrero fueron el 7.2% del total de los tickets.'
    elif id_grafica == 'bar-chart-7' and selected_date == '2024-02-13':
        return 'El 13 de febrero, las cinco tiendas registraron ID’s de clientes con más de un registro.'

app.layout = dbc.Container([
    navbar,
    html.Br(),
    html.Br(),

    # Filas para los totales de ID
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Tickets Acumulados desde el 6 de febrero", className="card-title"),
                    html.H3(id="total-ids", className="card-text")
                ])
            ], color="success", inverse=True)
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
            ], color="dodgerblue", inverse=True)
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Invalid ID", className="card-title"),
                    html.H3(id="total-invalid-id", className="card-text")
                ])
            ], color="warning", inverse=True)
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total No ID", className="card-title"),
                    html.H3(id="total-no-id", className="card-text")
                ])
            ], color="danger", inverse=True)
        ], width=4),
    ]),
    html.Br(),
    # Selector de fecha
    dbc.Row([
        dbc.Col(html.Div([
            html.Label("Seleccionar Fecha:   "),
            dcc.DatePickerSingle(
                id='date-picker',
                date=cobertura_por_fecha['Date'].iloc[0],
                display_format='YYYY-MM-DD'
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



    # Gráficos y explicaciones
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart'),
            html.Div(id='explicacion-bar-chart', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
        dbc.Col([
            dcc.Graph(id='bar-chart-2'),
            html.Div(id='explicacion-bar-chart-2', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
    ], style={'margin-bottom': '20px'}),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart-3'),
            html.Div(id='explicacion-bar-chart-3', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
        dbc.Col([
            dcc.Graph(id='bar-chart-4'),
            html.Div(id='explicacion-bar-chart-4', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
    ], style={'margin-bottom': '20px'}),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart-5'),
            html.Div(id='explicacion-bar-chart-5',style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
        dbc.Col([
            dcc.Graph(id='bar-chart-6'),
            html.Div(id='explicacion-bar-chart-6', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
    ], style={'margin-bottom': '20px'}),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart-7'),
            html.Div(id='explicacion-bar-chart-7', style={'font-size': '16px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),
        ], style={'list-style-type': 'circle', 'text-align': 'center'}),
    ], style={'margin-bottom': '20px'}),
    html.Br(),

], fluid=True)

# Callback para actualizar los totales de Status ID, Invalid ID y No ID
@app.callback(
    [Output('total-ids', 'children')],
    [Input('date-picker', 'date')]
)

def total_ids(selected_date):
    total_ids = df['Transaction Id.'].nunique()
    return [total_ids]

@app.callback(
    [Output('total-status-id', 'children'),
     Output('total-invalid-id', 'children'),
     Output('total-no-id', 'children')],
    [Input('date-picker', 'date')]
)
def update_totals(selected_date):
    total_status_id = df[df['Status'] == 'ID']['Transaction Id.'].nunique()
    total_invalid_id = df[df['Status'] == 'Invalid ID']['Transaction Id.'].nunique()
    total_no_id = df[df['Status'] == 'No ID']['Transaction Id.'].nunique()
    total_ids = df['Transaction Id.'].nunique()

    return total_status_id, total_invalid_id, total_no_id

# Callback para actualizar la tabla
@app.callback(
    Output('table-container', 'children'),
    [Input('date-picker', 'date')]
)

def update_table(selected_date):
    df_selected = cobertura_por_fecha[cobertura_por_fecha['Date'] == selected_date]
    cobertura_promedio_selected = cobertura_promedio[cobertura_promedio['Date'] == selected_date]['Coverage'].values[0]

    df_selected.loc[:, 'Coverage'] = (df_selected['Coverage'].round(0)).astype(int).astype(str) + '%'
    #print(cobertura_promedio_selected, '%')
    cobertura_promedio_selected = str(int(round(cobertura_promedio_selected))) + '%'

    total_tickets_sum = df_selected['Total_Tickets'].sum()
    total_tickets_id_sum = df_selected['Tickets_with_ID'].sum()

    df_selected = pd.concat([df_selected, pd.DataFrame({'Desc. Store': ['Promedio'], 'Total_Tickets': [total_tickets_sum], 'Tickets_with_ID':[total_tickets_id_sum],'Coverage': [cobertura_promedio_selected]})], ignore_index=True)

    table = dbc.Table.from_dataframe(
        df_selected,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )
    return table

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('date-picker', 'date')]
)

def update_bar_chart(selected_date):
    return create_bar_chart(selected_date)

@app.callback(
    Output('bar-chart-2','figure'),
    [Input('date-picker','date')]
)
def update_bar_chart_2(selected_date):
    return create_second_bar_chart(selected_date)

@app.callback(
    Output('bar-chart-3','figure'),
    [Input('date-picker','date')]
)
def update_bar_chart_3(selected_date):
    return create_bar_chart_id_pos(selected_date)
@app.callback(
    Output('bar-chart-4','figure'),
    [Input('date-picker','date')]
)
def update_bar_chart_2(selected_date):
    return create_bar_chart_noid_pos(selected_date)
@app.callback(
    Output('bar-chart-5','figure'),
    [Input('date-picker','date')]
)
def update_bar_chart_2(selected_date):
    return create_histogram_length(selected_date)

@app.callback(
    Output('bar-chart-6','figure'),
    [Input('date-picker','date')]
)
def update_bar_chart_2(selected_date):
    return create_bar_invalid(selected_date)

@app.callback(
    Output('bar-chart-7','figure'),
    [Input('date-picker','date')]
)
def update_bar_chart_2(selected_date):
    return create_bar_duplicated(selected_date)

# Paso 2: Actualizar el texto de explicación de cada gráfica según la fecha seleccionada

@app.callback(
    Output('explicacion-bar-chart', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart(selected_date):
    return obtener_explicacion_grafica('bar-chart', selected_date)

@app.callback(
    Output('explicacion-bar-chart-2', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_2(selected_date):
    return obtener_explicacion_grafica('bar-chart-2', selected_date)

@app.callback(
    Output('explicacion-bar-chart-3', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_3(selected_date):
    return obtener_explicacion_grafica('bar-chart-3', selected_date)
@app.callback(
    Output('explicacion-bar-chart-4', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_4(selected_date):
    return obtener_explicacion_grafica('bar-chart-4', selected_date)

@app.callback(
    Output('explicacion-bar-chart-5', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_5(selected_date):
    return obtener_explicacion_grafica('bar-chart-5', selected_date)

@app.callback(
    Output('explicacion-bar-chart-6', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_6(selected_date):
    return obtener_explicacion_grafica('bar-chart-6', selected_date)

@app.callback(
    Output('explicacion-bar-chart-7', 'children'),
    [Input('date-picker', 'date')]
)
def actualizar_explicacion_bar_chart_7(selected_date):
    return obtener_explicacion_grafica('bar-chart-7', selected_date)


if __name__ == '__main__':
    app.run_server(debug=True)
