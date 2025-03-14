import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import io
import base64
import os
import plotly.graph_objects as go
import plotly.express as px

import math


import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_leaflet as dl

#from dash_extensions import Download
#from dash_extensions.snippets import send_bytes
import io
from dash.dependencies import Input, Output, State

import folium


from datetime import datetime
from datetime import date



DTJ=date.today()
print(DTJ)

current_year = DTJ.strftime("%Y")
print("Année actuelle =", current_year)


# ## 2. Reporting dynamique (DASH)

# ### 2.1 / Manipulations des données

# In[269]:


# Chemin du fichier Excel
file_path = "02_INPUTS/_20250308_inputs_auto_ecole.xlsx"
print(file_path)


# Vérification de l'existence du fichier
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable !")



# Import du fichier Excel 
df = pd.read_excel(file_path,sheet_name="DATABASE")

df["Délais_inter_lecon"]=df["Délais_inter_lecon"].astype(int)
df=df.sort_values(by=["SCORE"],ascending=False)

# Conversion explicite des dates après la création du DataFrame
for col in ["Date_naissance", "Date_signature", "Date_obtention_code","Date_premiere_lecon", "Date_derniere_lecon"]:
    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
    

# Définition des catégories pour les graphiques
bins_signature = [0, 30, 60, 90, 180, 360, 720, float("inf")]
labels_signature = ["<30", "30-60", "60-90", "90-180", "180-360", "360-720", ">720"]
df["Cat_Signature"] = pd.cut(df["Anciennete_signature"], bins=bins_signature, labels=labels_signature, right=False)

bins_code = [0, 30, 60, 90, 120, float("inf")]
labels_code = ["<30", "30-60", "60-90", "90-120", ">120"]
df["Cat_Code"] = pd.cut(df["Anciennete_code"], bins=bins_code, labels=labels_code, right=False)



# Création du graphique en donut
df['Nb_presentations_code_group'] = df['Nb_presentations_code'].apply(lambda x: '1' if x == 1 else ('2' if x == 2 else ('3' if x == 3 else 'Plus de 3')))
donut_data = df['Nb_presentations_code_group'].value_counts().reset_index()
donut_data.columns = ['Nb_presentations_code_group', 'count']




print(df.shape)
df.head()


coords = {
    "Lille": [50.62925, 3.057256],
    "Mons-en-Baroeul": [50.6389, 3.0964],
    "Lezennes": [50.617, 3.106],
    "Ronchin": [50.5958, 3.0792],
    "Faches-Thumesnil": [50.5939, 3.0758],
    "Sainghin-en-Mélantois": [50.5686, 3.1547],
    "Villeneuve-d'Ascq": [50.6231, 3.1508]
}

map_carte = folium.Map(location=[50.617, 3.106], zoom_start=12)
df_localisation = df.groupby("Localisation").size().reset_index(name="Nombre")
for _, row in df_localisation.iterrows():
    if row['Localisation'] in coords:
        folium.Marker(
            location=coords[row['Localisation']],
            popup=f"{row['Localisation']}: {row['Nombre']} apprentis",
            icon=folium.Icon(color='blue')
        ).add_to(map_carte)

# Sauvegarde de la carte en HTML
map_html = "map.html"
map_carte.save(map_html)


# ### Import de l'onglet qui servira pour les ENCARTS

# In[273]:


# Import du fichier Excel 
encarts = pd.read_excel(file_path,sheet_name="ENCARTS")

# Mise au format %
encarts["parts_inscrits_AAC"]=((encarts["parts_inscrits_AAC"]*100).astype(int)).astype(str)+"%"

print(encarts["parts_inscrits_AAC"].dtype)
print(encarts.shape)
encarts.head()


# ### Import de l'onglet qui servira pour les GRAPHIQUES

# In[274]:


# Import du fichier Excel 
graphiques = pd.read_excel(file_path,sheet_name="GRAPHIQUES")

# Mise au format %
graphiques["Reussite_code"]=(graphiques["Reussite_code"]*100).astype(int)
graphiques["Réussite_conduite"]=(graphiques["Réussite_conduite"]*100).astype(int)

print(graphiques.shape)
graphiques.head(n=12)


# ### 2.2 / Représentation Dash


# Création des graphiques pour "graphiques"
fig_inscriptions = px.line(graphiques, x="Mois", y="Nb_inscriptions", markers=True)
fig_inscriptions.update_layout(title_text="Nombre d'inscriptions", title_x=0.5, showlegend=False, plot_bgcolor='#2C3E50', paper_bgcolor='#2C3E50', font=dict(color='white'), xaxis_title=None, yaxis_title=None,margin=dict(l=20, r=20, t=40, b=20))

fig_reussite = px.bar(x=["<30", "30-60", "60-90", "90-120", ">120"], y=[12, 18, 10, 22, 30])
fig_reussite.update_layout(title_text="Ancienneté Code (en jours)", title_x=0.5, showlegend=False, plot_bgcolor='#2C3E50', paper_bgcolor='#2C3E50', font=dict(color='white'), xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=40, b=20))

# Graphiques pour Ancienneté Signature et Code
fig_signature = px.bar(x=["<30", "30-60", "60-90", "90-180", "180-360", "360-720", ">720"], y=[10, 15, 8, 20, 25, 18, 5])
fig_signature.update_layout(title_text="Ancienneté Signature (en jours)", title_x=0.5, showlegend=False, plot_bgcolor='#2C3E50', paper_bgcolor='#2C3E50', font=dict(color='white'), xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=40, b=20))

fig_code = px.line(graphiques, x="Mois", y=["Reussite_code", "Réussite_conduite"], markers=True)
fig_code.update_layout(title_text="Taux de Réussite Code & Conduite", title_x=0.5, showlegend=False, plot_bgcolor='#2C3E50', paper_bgcolor='#2C3E50', font=dict(color='white'), xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=40, b=20))

fig_donut = px.pie(donut_data, names='Nb_presentations_code_group', values='count', hole=0.4, title="Présentations au code")
fig_donut.update_layout(title_x=0.5, showlegend=False, plot_bgcolor='#2C3E50', paper_bgcolor='#2C3E50', font=dict(color='white'), xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=40, b=20))


# Initialisation de l'application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Graphiques fig_signature, graph_code, graph_donut et graph_inscriptions mis à jour dynamiquement
graph_signature = dcc.Graph(id="graph_signature",figure=fig_signature,style={'width': '100%', 'height': '300px'})
graph_reussite = dcc.Graph(id="graph_reussite",figure=fig_reussite,style={'width': '100%', 'height': '300px'})
graph_donut = dcc.Graph(id="graph_donut",figure=fig_donut,style={'width': '100%', 'height': '300px'})
graph_inscriptions = dcc.Graph(figure=fig_inscriptions,style={'width': '100%', 'height': '300px'})
    
    
app.layout = dbc.Container(
    [
        # Encadrés d'information
        dbc.Row([
            dbc.Col(html.Div([
                html.P([
                    html.Span(f"{encarts['nb_inscrits_global'][0]} ", className="highlight"),
                    "inscrits actuellement dont ",
                    html.Span(f"{encarts['nb_inscrits_AAC'][0]} ", className="highlight"),
                    "en AAC soit ",
                    html.Span(f"{encarts['parts_inscrits_AAC'][0]}", className="highlight")
                ])
            ], className="info-box"), width=4),
            
            dbc.Col(html.Div([
                html.P([
                    html.Span(f"{encarts['nb_15h_25h'][0]} ", className="highlight"),
                    "élèves entre 15h et 25h de conduite."
                ])
            ], className="info-box"), width=4),
            
            # Menu déroulant pour filtrer par Localisation
            dbc.Col(html.Div([
                dcc.Dropdown(
                    id="dropdown-localisation",
                    options=[{"label": loc, "value": loc} for loc in sorted(df["Localisation"].unique())],
                    value=None,
                    placeholder="Sélectionnez une Localisation",
                    style={
                        'width': '100%', 
                        'font-size': '16px', 
                        'background-color': '#2C3E50',  
                        'color': 'white',  
                        'border': '1px solid #3498DB',  
                    },
                    className="custom-dropdown"
                )
            ], className="info-box"), width=4)
        ], className="g-3"),

        # Graphiques
        dbc.Row([
            dbc.Col(graph_signature, width=4, className="p-2"),
            dbc.Col(graph_reussite, width=4, className="p-2"),
            dbc.Col(graph_inscriptions, width=4, className="p-2")
        ], className="g-3"),

        # Ligne 2 : Colonne de gauche empilée avec fig_code et fig_donut, colonne de droite avec la carte
        dbc.Row([
            dbc.Col(graph_donut, width=4, className="p-2"),  
            dbc.Col(
                html.Iframe(srcDoc=open(map_html, 'r').read(), width='100%', height='300px'),
                width=8, className="p-2"
            )
        ], className="g-3")
    ],
    fluid=True,
    className="responsive-container"
)

# 📌 Callback pour filtrer `fig_donut` en fonction de la Localisation sélectionnée
@app.callback(
    Output("graph_donut", "figure"),
    [Input("dropdown-localisation", "value")]
)
def update_graph_donut(selected_location):
    dff = df.copy()
    if selected_location:
        dff = dff[dff["Localisation"] == selected_location]

    fig = px.pie(
        dff.groupby("Nb_presentations_code_group").size().reset_index(name="count"),
        names="Nb_presentations_code_group",
        values="count",
        hole=0.4,
        title="Présentations au code"
    )

    fig.update_layout(
        title_x=0.5,
        showlegend=True,  
        plot_bgcolor='#2C3E50',
        paper_bgcolor='#2C3E50',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10)
    )

    return fig


# Callback pour filtrer fig_signature en fonction de la Localisation sélectionnée
@app.callback(
    Output("graph_signature", "figure"),
    [Input("dropdown-localisation", "value")]
)
def update_graph_signature(selected_location):
    dff = df.copy()
    if selected_location:
        dff = dff[dff["Localisation"] == selected_location]
    
    fig = px.bar(
        dff.groupby("Cat_Signature").size().reset_index(name="count"),
        x="Cat_Signature", y="count",
        title="Ancienneté Signature"
    )

    fig.update_layout(
        title_x=0.5,
        showlegend=False,
        plot_bgcolor='#2C3E50',
        paper_bgcolor='#2C3E50',
        font=dict(color='white'),
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=10, r=10, t=40, b=10)  
    )

    return fig

# Callback pour filtrer fig_reussite en fonction de la Localisation sélectionnée
@app.callback(
    Output("graph_reussite", "figure"),
    [Input("dropdown-localisation", "value")]
)
def update_graph_reussite(selected_location):
    dff = df.copy()
    if selected_location:
        dff = dff[dff["Localisation"] == selected_location]

    # Création du graphique mis à jour
    fig = px.bar(
        x=["<30", "30-60", "60-90", "90-120", ">120"],
        y=[dff[dff["Cat_Code"] == "<30"].shape[0],
           dff[dff["Cat_Code"] == "30-60"].shape[0],
           dff[dff["Cat_Code"] == "60-90"].shape[0],
           dff[dff["Cat_Code"] == "90-120"].shape[0],
           dff[dff["Cat_Code"] == ">120"].shape[0]],
        title="Ancienneté Code (en jours)"
    )

    fig.update_layout(
        title_x=0.5,
        showlegend=False,
        plot_bgcolor='#2C3E50',
        paper_bgcolor='#2C3E50',
        font=dict(color='white'),
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=10, r=10, t=40, b=10)  
    )

    return fig



# CSS pour la mise en forme responsive
# Ajout du CSS pour améliorer le responsive
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mon Application Dash</title>
    {%metas%}
    {%favicon%}
    {%css%}
    <style>
        body { background-color: #d3d3d3; }
        .responsive-container { padding: 10px; }
        .info-box {
            font-weight: bold;
            font-size: 1.2rem;
            text-align: center;
            margin: 10px auto;
            padding: 15px;
            border-radius: 10px;
            background-color: #2C3E50;
            color: white;
            max-width: 90%;
        }
        @media (max-width: 768px) {
            .info-box { font-size: 1rem; }
            .g-3 .p-2 { padding: 5px !important; }
        }
    </style>
</head>
<body>
    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
</body>
</html>
'''


# Définir server pour Gunicorn
server = app.server  

# Récupération du port attribué par Render (ou 8050 par défaut en local)
port = int(os.environ.get("PORT", 8050))

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=port)
