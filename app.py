import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from geopy.distance import geodesic

# CONFIG
st.set_page_config(page_title="Détecteur Scout", layout="centered")
CIBLE_RADIUS_METERS = 500

# ZONES CIBLES GPS
points_cibles = [
    {"nom": "Spot 1", "coords": (50.68704115862972, 4.260554416777018)},
    {"nom": "Spot 2", "coords": (50.68141372627077, 4.264321702154752)},
    {"nom": "Spot 3", "coords": (50.68280545646507, 4.269052508141664)},
    {"nom": "Spot 4", "coords": (50.68180044491118, 4.258132598179554)},
    {"nom": "PlaceUNifTEST",     "coords": (50.66982006099279, 4.615156809327821)},
    {"nom": "CinéscopeTEST",     "coords": (50.66894905762168, 4.611584693290536)},
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

# === Bouton manuel de rafraîchissement via callback ===
def _reload():
    st.experimental_rerun()

st.button("📍 Recharger ma position", on_click=_reload)

# === Auto-refresh toutes les 10 secondes (JS) ===
st.markdown("""
<script>
    setTimeout(() => { window.location.reload(); }, 10000);
</script>
""", unsafe_allow_html=True)

# === Localisation GPS ===
coords = streamlit_js_eval(
    js_expressions="""
      navigator.geolocation.getCurrentPosition(
        pos => {
          Streamlit.setComponentValue({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude
          })
        },
        err => {
          Streamlit.setComponentValue({ error: err.message })
        }
      );
    """,
    key="get_position",
    want_output=True
)

# === Traitement des coordonnées ===
if isinstance(coords, dict) and "latitude" in coords and "longitude" in coords:
    lat, lon = coords["latitude"], coords["longitude"]
    user_loc = (lat, lon)

    distances = [
        (pt["nom"], geodesic(user_loc, pt["coords"]).meters)
        for pt in points_cibles
    ]
    nom_zone, distance_m = min(distances, key=lambda x: x[1])

    st.markdown(f"""
        <div class="box">
            <div class="info">
                📍 Position détectée<br><br>
                Distance de <b>{nom_zone}</b> : <b>{int(distance_m)} m</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if distance_m <= CIBLE_RADIUS_METERS:
        freq = max(0.3, 3 * (1 - distance_m / CIBLE_RADIUS_METERS))
        st.success(f"📡 Signal capté à {int(distance_m)} m ! Le radar s'affole...")
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

elif isinstance(coords, dict) and "error" in coords:
    st.error(f"📡 Erreur géoloc : {coords['error']}")

else:
    st.info("📍 En attente de localisation GPS…")
