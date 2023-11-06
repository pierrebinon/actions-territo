import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import urllib.request
import json
import geopandas as gpd

# paramètres
sheet_name = 'Synthèse pour DREAL (en caché)'
output_file_name='aggrégation.csv'
headers_number = 2
cols = ['Thème', 'Levier de décarbonation ',
       'Pertinence pour la collectivité \n1 = Pas du tout\n2 = Un peu \n3 = Beaucoup',
       'Action de la collectivité à la hauteur des enjeux\n1 = Plutôt non\n2 = Partiellement non\n3 = Partiellement oui\n4 = Plutôt oui',
       'Action collective à la hauteur des enjeux\n1 = Plutôt non\n2 = Partiellement non\n3 = Partiellement oui\n4 = Plutôt oui',
       'Unnamed: 5',
       'Indicateur d\'action en cours\n% d\'actions pertinentes réalisées\nun "!" indique lorsqu\'il y a une possible incohérence avec le pronostic sur l\'action de la collectivité',
       'Unnamed: 7', 'filename']
replace_by_nan = ['Non pertinent', 'Ne sait pas']

# Glissé déposé des fichiers
st.title("1. Envoyez les fichiers ici")
files = st.file_uploader('files', label_visibility='hidden', type=['xlsx','xls'], accept_multiple_files=True)

# Aggrégation des fichiers
if files is not None and len(files) > 0:
    df = pd.DataFrame()
    for f in files:
        try:
            sheet = pd.read_excel(f, sheet_name=sheet_name, header=headers_number)
            if len(sheet) == 0:
                st.error("Le fichier '" + f.name + "' ne contient pas la page '" + sheet_name + "'")
            else:
                sheet['filename'] = f.name
                # replace values by NaN
                sheet = sheet.replace(replace_by_nan, np.nan)
                df = pd.concat([df, sheet])
        except ValueError:
            st.error("Le fichier " + f.name + " ne contient pas la page " + sheet_name)

    st.write("---")
    st.title("2. Télécharger le fichier aggrégé")
    st.download_button(label="Télécharger",data=df.to_csv(index=False),file_name=output_file_name,mime='text/csv')
    st.dataframe(df.groupby(['Thème', 'Levier de décarbonation ']).mean())

    # display france mapbox
    st.write("---")
    st.title("3. Afficher la carte de France")
    
    with urllib.request.urlopen("https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson") as url:
        french_departments_geojson = json.loads(url.read().decode())

    # geojson to geopandas
    gdf = gpd.GeoDataFrame.from_features(french_departments_geojson["features"])

    # display the gdf polygons on a map
    fig = px.choropleth_mapbox(
        gdf, 
        geojson=gdf.geometry, 
        locations=gdf.index, 
        #color="index",
        #hover_name="nom",
        #hover_data=["nom"],
        mapbox_style="carto-positron",
        zoom=4, 
        center={"lat": 46.7111, "lon": 1.7191},
        opacity=0.5,
        labels={"index":"Département"}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    
    





