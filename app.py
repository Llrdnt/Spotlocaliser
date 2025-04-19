import streamlit as st
from geopy.distance import geodesic
from streamlit_folium import st_folium
import folium
import time

# CONFIG
st.set_page_config(page_title="Détecteur Scout", layout="centered")
CIBLE_RADIUS_METERS = 500

# ZONES CIBLES GPS
points_cibles = [
    {"nom": "Caverne du castor ⛰️", "coords": (50.686760, 4.260713)},
    {"nom": "Cabane de la meute 🛖", "coords": (50.681436, 4.264436)},
    {"nom": "Tente de la troupe 🏕️", "coords": (50.682358, 4.266773)},
    {"nom": "Base de vie - EBB", "coords": (50.681244, 4.264599)},
]

# STYLES
st.markdown("""
    <style>
    body {
        background-color: #f9fdfc;
    }
    .title {
        font-size: 2.5em;
        text-align: center;
        margin-top: 1em;
        font-weight: bold;
        color: #1b4332;
        font-family: 'Segoe UI', sans-serif;
    }
    .box {
        background-color: #d8f3dc;
        padding: 1.5em;
        border-radius: 15px;
        margin-top: 1em;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        font-size: 1.1em;
    }
    .spot-box {
        background: linear-gradient(135deg, #ffffff 0%, #e9f5ee 100%);
        border-left: 6px solid #52b788;
        border-radius: 10px;
        padding: 1em;
        margin: 1em 0;
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.05);
    }
    .spot-box b {
        font-size: 1.2em;
        color: #081c15;
    }
    .distance {
        font-weight: bold;
        font-size: 1.1em;
        color: #40916c;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Détecteurs des caches secrètes 🧌</div>', unsafe_allow_html=True)

# Initialiser la session state
if 'position' not in st.session_state:
    st.session_state.position = None

# Carte avec folium (centrée arbitrairement)
centre_carte = [50.670, 4.615]
m = folium.Map(location=centre_carte, zoom_start=13)
folium.plugins.LocateControl(auto_start=True).add_to(m)
map_data = st_folium(m, height=2, width=2)

# Détection automatique de la position via le centre de la carte
if map_data and 'center' in map_data and map_data['center']:
    lat = map_data['center']['lat']
    lon = map_data['center']['lng']
    st.session_state.position = (lat, lon)

# Affichage principal
if st.session_state.position:
    user_loc = st.session_state.position
    st.markdown(f"""
        <div class=\"box\">
            📍 Position actuelle détectée<br>
            <b>Latitude:</b> {user_loc[0]:.6f}, <b>Longitude:</b> {user_loc[1]:.6f}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top:2em; color: #1b4332;'>🗺️ Votre distance par rapport aux caches</h3>", unsafe_allow_html=True)

    for spot in points_cibles:
        distance = geodesic(user_loc, spot["coords"]).meters
        st.markdown(f"""
            <div class=\"spot-box\">
                <b>{spot['nom']}</b><br>
                Distance: <span class='distance'>{int(distance)} m</span>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("📡 Position non détectée. Activez la localisation sur votre appareil pour la détection automatique.")


st.markdown("""
    <div style='margin-top: 3em; text-align: center;'>
        <img src='https://github.com/Llrdnt/Spotlocaliser/blob/main/BRENCHATOBIS.png?raw=true' style='max-width: 60%; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);' alt='Image décorative'>
    </div>
""", unsafe_allow_html=True)
