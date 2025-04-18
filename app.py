import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.title("Test localisation GPS")

coords = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition((pos) => {const coords = pos.coords.latitude + ',' + pos.coords.longitude; Streamlit.setComponentValue(coords);});",
    key="get_position_test"
)

if coords:
    st.success(f"Position : {coords}")
else:
    st.info("En attente de la localisation...")
