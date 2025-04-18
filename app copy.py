import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
from geopy.distance import geodesic
import time

# CONFIG
st.set_page_config(page_title="Détecteur Scout", layout="centered")
CIBLE_RADIUS_METERS = 500

# Vérifie que streamlit-folium est installé
try:
    import streamlit_folium
except ImportError:
    st.error("Ce script nécessite la bibliothèque 'streamlit-folium'. Installez-la avec: pip install streamlit-folium")
    st.stop()

# ZONES CIBLES GPS
points_cibles = [
    {"nom": "Spot 1", "coords": (50.68704115862972, 4.260554416777018)},
    {"nom": "Spot 2", "coords": (50.68141372627077, 4.264321702154752)},
    {"nom": "Spot 3", "coords": (50.68280545646507, 4.269052508141664)},
    {"nom": "Spot 4", "coords": (50.68180044491118, 4.258132598179554)},
    {"nom": "PlaceUNifTEST", "coords": (50.66982006099279, 4.615156809327821)},
    {"nom": "CinéscopeTEST", "coords": (50.66894905762168, 4.611584693290536)},
]

# UI STYLES
st.markdown("""
    <style>
    .title { font-size: 2em; text-align: center; margin-top: 1em; font-weight: bold; color: #2b4a2d; }
    .box   { background-color: #e5f5e0; padding: 1em; border-radius: 10px; margin-top: 1em;
             text-align: center; box-shadow: 0px 0px 10px #ccc; }
    .info  { font-size: 1.2em; margin-top: 1em; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧭 Détecteur de balises cachées</div>', unsafe_allow_html=True)

# Initialiser la session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'position' not in st.session_state:
    st.session_state.position = None

# Centre approximatif pour démarrer (si pas de position)
centre_carte = [50.670, 4.615]  # Centre approximatif

# Bouton de localisation
if st.button("📍 Localiser ma position", key="locate_me"):
    st.session_state.last_update = time.time()
    # La localisation est gérée par folium

# Rafraîchissement automatique
if time.time() - st.session_state.last_update > 30:  # Auto-refresh toutes les 30 secondes
    st.session_state.last_update = time.time()
    st.rerun()

# Créer la carte
m = folium.Map(location=centre_carte, zoom_start=13)

# Ajouter le bouton de localisation à la carte
folium.LatLngPopup().add_to(m)
folium.plugins.LocateControl(
    auto_start=True,
    flyTo=True,
    keepCurrentZoomLevel=True,
    strings={"title": "Ma position", "popup": "Vous êtes ici"}
).add_to(m)

# Obtenir la position avec st_folium
map_data = st_folium(m, height=300, width=600)

# Traiter la position de l'utilisateur
user_position = None
if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
    # Position basée sur un clic de l'utilisateur
    user_position = [map_data['last_clicked']['lat'], map_data['last_clicked']['lng']]
    st.session_state.position = user_position
elif map_data and 'center' in map_data and map_data['center']:
    # Position basée sur le centre actuel de la carte (peut être défini par le contrôle de localisation)
    user_position = [map_data['center']['lat'], map_data['center']['lng']]
    if st.session_state.position is None:  # Ne pas écraser la position existante
        st.session_state.position = user_position

# Si nous avons une position (soit par clic, soit par le centre de la carte)
if st.session_state.position:
    user_lat, user_lon = st.session_state.position
    user_loc = (user_lat, user_lon)
    
    # Calcul des distances
    distances = [
        (pt["nom"], geodesic(user_loc, pt["coords"]).meters)
        for pt in points_cibles
    ]
    nom_zone, distance_m = min(distances, key=lambda x: x[1])

    st.markdown(f"""
        <div class="box">
            <div class="info">
                📍 Position détectée<br><br>
                Distance de <b>{nom_zone}</b> : <b>{int(distance_m)} m</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if distance_m <= CIBLE_RADIUS_METERS:
        freq = max(0.3, 3 * (1 - distance_m / CIBLE_RADIUS_METERS))
        st.success(f"📡 Signal capté à {int(distance_m)} m ! Le radar s'affole...")
        st.markdown(f"""
        <audio id="bip" autoplay loop>
            <source src="https://www.soundjay.com/button/beep-07.wav" type="audio/wav">
        </audio>
        <script>
        const bip = document.getElementById("bip");
        setInterval(() => {{
            bip.pause();
            bip.currentTime = 0;
            bip.play();
        }}, {int(freq * 1000)});
        </script>
        """, unsafe_allow_html=True)
    else:
        st.warning("🔕 Aucun signal détecté dans cette zone…")
    
    # Afficher les coordonnées en mode debug
    with st.expander("Détails techniques"):
        st.write(f"Latitude: {user_lat}")
        st.write(f"Longitude: {user_lon}")

else:
    st.info("""
    **Instructions:**
    1. Cliquez sur le bouton de localisation 🔍 dans la carte pour trouver votre position
    2. Ou cliquez sur la carte pour sélectionner un emplacement manuellement
    """)