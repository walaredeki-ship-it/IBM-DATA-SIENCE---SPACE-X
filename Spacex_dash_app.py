# Import des bibliothèques requises
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Chargement du jeu de données SpaceX
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Création de l'application Dash
app = dash.Dash(__name__)

# --- SECTION 1 : CONFIGURATION DU LAYOUT (L'INTERFACE GRAPHIQUE) ---
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-family': 'Arial', 'fontSize': 40}),
    
    # TASK 1: Ajout du menu déroulant pour les sites de lancement
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'font-family': 'Arial'}
    ),
    html.Br(),

    # Emplacement pour le graphique en secteurs (Pie Chart) de la TASK 2
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'font-family': 'Arial', 'fontSize': 18}),
    
    # TASK 3: Ajout du curseur d'intervalle pour la masse de la charge utile (Range Slider)
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Emplacement pour le nuage de points (Scatter Chart) de la TASK 4
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# --- SECTION 2 : CONFIGURATION DES CALLBACKS (LA LOGIQUE INTERACTIVE) ---

# TASK 2: Callback pour mettre à jour le Pie Chart en fonction du site sélectionné
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Si 'ALL' est choisi, on montre la répartition globale des succès de CHAQUE site
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By All Sites'
        )
        return fig
    else:
        # Si un site spécifique est choisi, on filtre et on montre le ratio de Succès (1) vs Échec (0)
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Décompte des succès et échecs pour ce site précis
        df_counts = filtered_df['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']
        
        fig = px.pie(
            df_counts, 
            values='count', 
            names='class', 
            title=f'Total Success Launches for Site {entered_site}',
            color='class',
            color_discrete_map={1: '#2ca02c', 0: '#d62728'} # Vert pour le succès, rouge pour l'échec
        )
        return fig


# TASK 4: Callback pour mettre à jour le Scatter Chart en fonction du site et du poids (Intervalle)
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(entered_site, payload_range):
    # Filtrer le dataframe par rapport aux valeurs du curseur de poids (RangeSlider)
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        # Nuage de points global
        fig = px.scatter(
            filtered_df, 
            x="Payload Mass (kg)", 
            y="class", 
            color="Booster Version Category",
            title="Correlation between Payload and Success for all Sites"
        )
        return fig
    else:
        # Nuage de points restreint au site sélectionné
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df, 
            x="Payload Mass (kg)", 
            y="class", 
            color="Booster Version Category",
            title=f"Correlation between Payload and Success for Site {entered_site}"
        )
        return fig

# Lancement de l'application locale
if __name__ == '__main__':
    app.run()