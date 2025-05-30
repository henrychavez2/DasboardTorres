import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, UTC

from data_handler import save_supabase
from weather_api import get_weather

app = dash.Dash(__name__)
app.title = "Dashboard Meteorológico"

# Diccionario para guardar datos históricos por ciudad
city_data = {}

def get_city_series(city):
    if city not in city_data:
        city_data[city] = {"x": [], "temp": [], "humedad": []}
    return city_data[city]

# Layout principal
app.layout = html.Div([
    html.H1("Monitoreo de Torres Meteorológicas"),

    html.Div([
        html.Label("Selecciona una ciudad:"),
        dcc.Dropdown(
            id='ciudad-dropdown',
            options=[
                {'label': 'Madrid', 'value': 'Madrid'},
                {'label': 'Buenos Aires', 'value': 'Buenos Aires'},
                {'label': 'Lima', 'value': 'Lima'},
                {'label': 'México DF', 'value': 'Mexico'},
                {'label': 'Bogotá', 'value': 'Bogota'},
                {'label': 'Santiago', 'value': 'Santiago'}
            ],
            value='Madrid',
            clearable=False,
            style={'width': '300px'}
        )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.H3("Temperatura (°C)", style={'textAlign': 'center'}),
                dcc.Graph(id='temp-graph')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                html.H3("Humedad (%)", style={'textAlign': 'center'}),
                dcc.Graph(id='humedad-graph')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),


    dcc.Interval(id='intervalo', interval=5000, n_intervals=0)
])

# Callback que actualiza ambas gráficas
@app.callback(
    [Output('temp-graph', 'figure'),
     Output('humedad-graph', 'figure')],
    [Input('intervalo', 'n_intervals'),
     Input('ciudad-dropdown', 'value')]
)
def update_graph(n, ciudad):
    try:
        timestamp = datetime.now(UTC).isoformat()
        temp, humedad = get_weather(ciudad)

        if temp is None or humedad is None:
            print(f"Datos inválidos recibidos para {ciudad}")
            return dash.no_update, dash.no_update

        # Guardar en Supabase
        data = (ciudad, timestamp, temp, humedad)
        save_supabase(data)

        # Guardar para graficar
        series = get_city_series(ciudad)
        series["x"].append(timestamp)
        series["temp"].append(temp)
        series["humedad"].append(humedad)

        # Gráfica de temperatura
        fig_temp = {
            'data': [{'x': series["x"], 'y': series["temp"], 'type': 'line', 'name': 'Temperatura (°C)', 'line':{ 'color':'green'}}],
            'layout': {'title': f'Temperatura en {ciudad}'}
        }

        # Gráfica de humedad
        fig_humedad = {
            'data': [{'x': series["x"], 'y': series["humedad"], 'type': 'line' , 'name': 'Humedad (%)'}],
            'layout': {'title': f'Humedad en {ciudad}'}
        }

        return fig_temp, fig_humedad

    except Exception as e:
        print(f"Error en update_graph: {e}")
        return dash.no_update, dash.no_update

if __name__ == '__main__':
    app.run(debug=True)
