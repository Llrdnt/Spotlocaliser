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
    {"nom": "Spot 1", "coords": (50.68704115862972, 4.260554416777018)},
    {"nom": "Spot 2", "coords": (50.68141372627077, 4.264321702154752)},
    {"nom": "Spot 3", "coords": (50.68280545646507, 4.269052508141664)},
    {"nom": "Spot 4", "coords": (50.68180044491118, 4.258132598179554)},
    {"nom": "PlaceUNifTEST", "coords": (50.66982006099279, 4.615156809327821)},
    {"nom": "CinéscopeTEST", "coords": (50.66894905762168, 4.611584693290536)},
]

# STYLES
st.markdown("""
    <style>
    .title { font-size: 2em; text-align: center; margin-top: 1em; font-weight: bold; color: #2b4a2d; }
    .box   { background-color: #e5f5e0; padding: 1em; border-radius: 10px; margin-top: 1em;
             text-align: center; box-shadow: 0px 0px 10px #ccc; }
    .spot-box { background-color: #ffffff; border: 2px solid #4CAF50; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📍 Répertoire des Spots</div>', unsafe_allow_html=True)

# Initialiser la session state
if 'position' not in st.session_state:
    st.session_state.position = None

# Carte avec folium (centrée arbitrairement)
centre_carte = [50.670, 4.615]
m = folium.Map(location=centre_carte, zoom_start=13)

# Ajout du contrôle de localisation auto
folium.plugins.LocateControl(auto_start=True).add_to(m)

# Intégration de la carte dans Streamlit
map_data = st_folium(m, height=300, width=600)

# Détection automatique de la position via le centre de la carte
if map_data and 'center' in map_data and map_data['center']:
    lat = map_data['center']['lat']
    lon = map_data['center']['lng']
    st.session_state.position = (lat, lon)

# Zone d'information utilisateur
if st.session_state.position:
    user_loc = st.session_state.position
    st.markdown(f"""
        <div class=\"box\">
            ✅ Position actuelle détectée :
            <br><b>Latitude:</b> {user_loc[0]:.6f}, <b>Longitude:</b> {user_loc[1]:.6f}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top:2em;'>🗺️ Distances jusqu'aux spots :</h3>", unsafe_allow_html=True)

    for spot in points_cibles:
        distance = geodesic(user_loc, spot["coords"]).meters
        st.markdown(f"""
            <div class=\"spot-box\">
                <b>{spot['nom']}</b><br>
                Distance: <span style='color:#4CAF50; font-weight:bold;'>{int(distance)} m</span>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("📡 Position non détectée. Activez la localisation sur votre appareil pour la détection automatique.")
