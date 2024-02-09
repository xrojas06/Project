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
df = pd.read_csv('update_report.csv')
df['Date'] = pd.to_datetime(df['Date'])
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
cobertura_promedio = cobertura_por_fecha.groupby('Date')['Coverage'].mean().reset_index()

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
        go.Bar(name='Pos 1', x=grouped_data.index, y=grouped_data[1], text=grouped_data[1], textposition='auto', insidetextanchor='end'),
        go.Bar(name='Pos 2', x=grouped_data.index, y=grouped_data[2], text=grouped_data[2], textposition='auto', insidetextanchor='end'),
        go.Bar(name='Pos 3', x=grouped_data.index, y=grouped_data[3], text=grouped_data[3], textposition='auto', insidetextanchor='end'),
        go.Bar(name='Pos 4', x=grouped_data.index, y=grouped_data[4], text=grouped_data[4], textposition='auto', insidetextanchor='end')
    ])

    # Agregar título y etiquetas de los ejes
    fig.update_layout(title='Cantidad de ID',
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
        go.Bar(name='Pos 1', x=grouped_data.index, y=grouped_data[1], text=grouped_data[1], textposition='auto', insidetextanchor='end'),
        go.Bar(name='Pos 2', x=grouped_data.index, y=grouped_data[2], text=grouped_data[2], textposition='auto', insidetextanchor='end'),
        go.Bar(name='Pos 3', x=grouped_data.index, y=grouped_data[3], text=grouped_data[3], textposition='auto', insidetextanchor='end'),
        go.Bar(name='Pos 4', x=grouped_data.index, y=grouped_data[4], text=grouped_data[4], textposition='auto', insidetextanchor='end')
    ])

    # Agregar título y etiquetas de los ejes
    fig.update_layout(title='Cantidad de No ID',
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



app.layout = dbc.Container([
    navbar,
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Status ID", className="card-title"),
                    html.H3(id="total-status-id", className="card-text")
                ])
            ], color="success", inverse=True)
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
    dbc.Row([
        dbc.Col([
            html.Label("Seleccionar Fecha:   "),
            dcc.DatePickerSingle(
                id='date-picker',
                date=cobertura_por_fecha['Date'].iloc[0],
                display_format='YYYY-MM-DD'
            ),
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(html.Div(id='table-container')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart-2')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart-3')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart-4')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart-5')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart-6')),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart-7')),
    ]),
], fluid=True)

# Callback para actualizar los totales de Status ID, Invalid ID y No ID
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



if __name__ == '__main__':
    app.run_server(debug=True)
