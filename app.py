import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
from geopy.distance import geodesic
import time
import requests

# CONFIG
st.set_page_config(page_title="Détecteur Scout", layout="centered")
CIBLE_RADIUS_METERS = 500

# ZONES CIBLES GPS
points_cibles = [
    {"nom": "Spot 1", "coords": (50.68704115862972, 4.260554416777018)},
    {"nom": "Spot 2", "coords": (50.68141372627077, 4.264321702154752)},
    {"nom": "Spot 3", "coords": (50.68280545646507, 4.269052508141664)},
    {"nom": "Spot 4", "coords": (50.68180044491118, 4.258132598179554)},
    {"nom": "Test", "coords": (50.666145486863286,4.278810154822357)},
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
    .no-gps { background-color: #f8d7da; padding: 1em; border-radius: 10px; margin-top: 1em;
              text-align: center; box-shadow: 0px 0px 10px #ccc; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧭 Détecteur de balises cachées</div>', unsafe_allow_html=True)

# Initialiser la session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'position' not in st.session_state:
    st.session_state.position = None
if 'gps_active' not in st.session_state:
    st.session_state.gps_active = False

# Centre approximatif pour démarrer
centre_carte = [50.670, 4.615]

# Rafraîchissement automatique
if time.time() - st.session_state.last_update > 30:
    st.session_state.last_update = time.time()
    st.rerun()

# Créer la carte
m = folium.Map(location=centre_carte, zoom_start=13)

# Ajouter les contrôles
folium.LatLngPopup().add_to(m)
folium.plugins.LocateControl(
    auto_start=True,
    flyTo=True,
    keepCurrentZoomLevel=True,
    strings={"title": "Ma position", "popup": "Vous êtes ici"}
).add_to(m)

# Récupérer données de la carte
map_data = st_folium(m, height=300, width=600)
st.write("Map data debug:", map_data)

# Récupérer la position automatiquement via le centre de la carte (LocateControl auto_start)
user_position = None

if map_data:
    if map_data.get('last_clicked'):
        user_position = [
            map_data['last_clicked']['lat'],
            map_data['last_clicked']['lng']
        ]
    elif map_data.get('center'):
        user_position = [
            map_data['center']['lat'],
            map_data['center']['lng']
        ]

if user_position:
    st.session_state.position = user_position
    st.session_state.gps_active = True


# Détection automatique de position
user_position = None
if map_data and 'location' in map_data and map_data['location']:
    user_position = [map_data['location']['lat'], map_data['location']['lng']]
    st.session_state.position = user_position
    st.session_state.gps_active = True

# Erreur si GPS demandé mais non dispo
if st.session_state.gps_active and not st.session_state.position:
    st.markdown("""
        <div class="no-gps">
            <div class="info">
                ⚠️ <b>Aucun signal GPS détecté</b> ⚠️<br><br>
                Vérifiez que la localisation est activée sur votre appareil
            </div>
        </div>
    """, unsafe_allow_html=True)

# Si position dispo
if st.session_state.position:
    user_lat, user_lon = st.session_state.position
    user_loc = (user_lat, user_lon)
    with st.expander("Distances à tous les spots"):
        for pt in points_cibles:
            dist = geodesic(user_loc, pt["coords"]).meters
            st.write(f"{pt['nom']}: {int(dist)} m")

    # Reset bip à chaque rafraîchissement
    st.session_state['bip_played'] = False

    # Calcul des distances
    distances = [
        (pt["nom"], geodesic(user_loc, pt["coords"]).meters)
        for pt in points_cibles
    ]
    nom_zone, distance_m = min(distances, key=lambda x: x[1])

    if distance_m <= CIBLE_RADIUS_METERS:
        freq = max(0.2, 2 * (distance_m / CIBLE_RADIUS_METERS))
        
        # Affichage infos
st.markdown(f"""
    <div class="box">
        <div class="info">
            📍 Position détectée<br><br>
            <b>Signal détecté!</b> Vous êtes à <b>{int(distance_m)} m</b> de <b>{nom_zone}</b>
        </div>
    </div>
""", unsafe_allow_html=True)

st.success(f"📡 Signal capté ! Le radar s'affole...")

# Charger et jouer le bip (via Streamlit)
if 'bip_played' not in st.session_state or not st.session_state['bip_played']:
    try:
        audio_url = "https://www.soundjay.com/button/beep-07.wav"
        audio_data = requests.get(audio_url).content
        st.audio(audio_data, format='audio/wav')
        st.session_state['bip_played'] = True
    except Exception as e:
        st.error("Erreur audio : " + str(e))

    else:
        st.markdown(f"""
            <div class="box">
                <div class="info">
                    📍 Position détectée<br><br>
                    🔕 Aucun signal détecté dans cette zone...
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning("🔕 Vous n'êtes à proximité d'aucun spot. Continuez d'explorer!")

    with st.expander("Détails techniques"):
        st.write(f"Latitude: {user_lat}")
        st.write(f"Longitude: {user_lon}")
        st.write(f"Spot le plus proche: {nom_zone}")
        st.write(f"Distance: {int(distance_m)} mètres")

else:
    st.info("""
    **Instructions:**
    - Donnez l'autorisation de localisation à votre navigateur.
    - Approchez-vous d'un des spots pour déclencher le signal.
    """)

# Liste des spots
with st.expander("Voir tous les spots (Admin)"):
    st.markdown("### Liste des spots à découvrir")
    for i, spot in enumerate(points_cibles):
        st.markdown(f'📌 <b>{spot["nom"]}</b>', unsafe_allow_html=True)
