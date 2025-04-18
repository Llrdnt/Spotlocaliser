import streamlit as st
from geopy.distance import geodesic
import json

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

# UI STYLES
st.markdown("""
    <style>
    .title { font-size: 2em; text-align: center; margin-top: 1em; font-weight: bold; color: #2b4a2d; }
    .box   { background-color: #e5f5e0; padding: 1em; border-radius: 10px; margin-top: 1em;
             text-align: center; box-shadow: 0px 0px 10px #ccc; }
    .info  { font-size: 1.2em; margin-top: 1em; }
    #location_display { margin: 20px 0; padding: 10px; background-color: #f0f9ff; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧭 Détecteur de balises cachées</div>', unsafe_allow_html=True)

# Injecter le JavaScript pour la géolocalisation directement
st.markdown("""
<div id="location_display">Attente de localisation...</div>

<script>
// Fonction pour mettre à jour la localisation et rafraîchir
function updateLocation() {
    const locationDisplay = document.getElementById('location_display');
    locationDisplay.innerHTML = "Demande de géolocalisation...";
    
    if (!navigator.geolocation) {
        locationDisplay.innerHTML = "La géolocalisation n'est pas supportée par votre navigateur.";
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // Créer un élément caché pour stocker les coordonnées
            let hiddenInput = document.getElementById('geolocation_data');
            if (!hiddenInput) {
                hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.id = 'geolocation_data';
                document.body.appendChild(hiddenInput);
            }
            
            // Stocker les coordonnées
            hiddenInput.value = JSON.stringify({
                latitude: lat,
                longitude: lon,
                accuracy: position.coords.accuracy
            });
            
            // Rediriger avec les coordonnées en paramètres
            window.location.href = `?lat=${lat}&lon=${lon}&acc=${position.coords.accuracy}`;
        },
        function(error) {
            let errorMsg;
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = "Accès à la géolocalisation refusé.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = "Localisation indisponible.";
                    break;
                case error.TIMEOUT:
                    errorMsg = "Délai de localisation expiré.";
                    break;
                default:
                    errorMsg = "Erreur inconnue de géolocalisation.";
            }
            locationDisplay.innerHTML = `Erreur: ${errorMsg}`;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// Démarrer la géolocalisation dès le chargement
updateLocation();

// Rafraîchir périodiquement
setInterval(updateLocation, 15000);
</script>
""", unsafe_allow_html=True)

# Récupérer les paramètres d'URL avec la nouvelle méthode recommandée
params = st.query_params
lat = params.get("lat", [""])[0] if "lat" in params else ""
lon = params.get("lon", [""])[0] if "lon" in params else ""
acc = params.get("acc", [""])[0] if "acc" in params else ""

# Bouton de rafraîchissement manuel
if st.button("📍 Actualiser ma position", key="reload_btn"):
    st.markdown("""
    <script>
        updateLocation();
    </script>
    """, unsafe_allow_html=True)
    st.rerun()

# Traitement des coordonnées si disponibles
if lat and lon and lat != "" and lon != "":
    try:
        lat = float(lat)
        lon = float(lon)
        user_loc = (lat, lon)
        
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
            st.write(f"Latitude: {lat}")
            st.write(f"Longitude: {lon}")
            if acc:
                st.write(f"Précision: ±{acc} mètres")

    except Exception as e:
        st.error(f"Erreur lors du traitement des coordonnées: {e}")
else:
    st.info("En attente de localisation... Si rien ne se passe, vérifiez les autorisations de votre navigateur.")
    
    # Instructions pour l'utilisateur
    with st.expander("Aide - Comment autoriser la géolocalisation"):
        st.markdown("""
        ### Comment autoriser la géolocalisation
        
        #### Sur Chrome/Edge:
        1. Cliquez sur l'icône du cadenas à gauche de l'URL dans la barre d'adresse
        2. Dans les paramètres du site, assurez-vous que "Localisation" est réglée sur "Autoriser"
        
        #### Sur Firefox:
        1. Cliquez sur l'icône du cadenas à gauche de l'URL
        2. Cliquez sur "Autorisations du site"
        3. Assurez-vous que "Accéder à votre localisation" est autorisé
        
        #### Sur Safari:
        1. Allez dans Préférences > Sites web > Localisation
        2. Autorisez ce site
        
        #### Sur mobile:
        1. Assurez-vous que la localisation est activée dans les paramètres de votre appareil
        2. Autorisez le navigateur à accéder à votre localisation
        
        **Important**: Cette application nécessite HTTPS pour fonctionner.
        """)