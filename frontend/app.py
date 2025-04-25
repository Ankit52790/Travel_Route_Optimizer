import streamlit as st
import requests, json
from opencage.geocoder import OpenCageGeocode
import pandas as pd
import pydeck as pdk
import folium
from streamlit_folium import st_folium
import math

# 1️⃣ Must be the very first Streamlit command
st.set_page_config(
    page_title="Travel Route Optimizer",
    page_icon="🚗",
    layout="wide"
)

# 🔑 OpenCage API key
OPENCAGE_API_KEY = "45b3f677b64f45d6bdc827723d813f9a"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

# Haversine for distance calculation
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

st.title("🚗 Travel Route Optimizer")
st.markdown("Enter city names, click on map, or both to add locations.")

# Session state for locations
if "all_locations" not in st.session_state:
    st.session_state.all_locations = []

# --- City input form ---
with st.form("city_form"):
    city_name = st.text_input("Enter City Name", placeholder="e.g., Delhi")
    add_by_name = st.form_submit_button("➕ Add by Name")
    if add_by_name and city_name:
        try:
            results = geocoder.geocode(city_name)
            if results:
                lat = results[0]["geometry"]["lat"]
                lng = results[0]["geometry"]["lng"]
                st.session_state.all_locations.append({"lat": lat, "lng": lng})
                st.success(f"✅ {city_name} added: {lat}, {lng}")
            else:
                st.warning("❗ No coordinates found for that city.")
        except Exception as e:
            st.error(f"⚠️ Geocoding error: {e}")

# --- Map click input ---
st.markdown("### 🗺️ Add location by clicking on the map")
m = folium.Map(location=[20, 78], zoom_start=5)
# Configure folium map to capture click events
m.add_child(folium.LatLngPopup())  # shows lat/lng on click

map_data = st_folium(m, width=700, height=400)
if map_data and map_data.get("last_clicked"):
    loc = map_data["last_clicked"]
    lat, lng = loc["lat"], loc["lng"]
    st.write(f"Clicked location: {lat:.6f}, {lng:.6f}")
    if st.button("➕ Add clicked location"):
        st.session_state.all_locations.append({"lat": lat, "lng": lng})
        st.success(f"✅ Added clicked location: {lat:.6f}, {lng:.6f}")

# --- Show added locations ---
if st.session_state.all_locations:
    st.markdown("### 📍 Added Locations:")
    for i, loc in enumerate(st.session_state.all_locations, 1):
        st.write(f"{i}. Latitude: {loc['lat']}, Longitude: {loc['lng']}")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🧮 Optimize Route"):
            with st.spinner("Optimizing..."):
                # Optimize via backend
                res = requests.post(
                    "http://localhost:8000/optimize",
                    json={"locations": st.session_state.all_locations}
                )
                if not res.ok:
                    st.error(f"API Error: {res.text}")
                    st.stop()
                optimized = res.json().get("route", [])
                if not optimized:
                    st.warning("⚠️ No route returned. Add more locations and try again.")
                    st.stop()
                st.success("✅ Optimized Route:")

                # Build DataFrame
                if isinstance(optimized[0], dict):
                    df = pd.DataFrame(optimized).rename(columns={"lng": "lon"})
                else:
                    df = pd.DataFrame(optimized, columns=["lat", "lon"])

                # Display ordered list
                for idx, row in df.iterrows():
                    st.write(f"{idx+1}. Lat: {row.lat}, Lon: {row.lon}")

                # Calculate distances
                distances = []
                for i in range(len(df)-1):
                    d = haversine(
                        df.loc[i, "lat"], df.loc[i, "lon"],
                        df.loc[i+1, "lat"], df.loc[i+1, "lon"]
                    )
                    distances.append(d)
                total_dist = sum(distances)
                st.markdown("**Segment Distances (km):**")
                for idx, d in enumerate(distances, 1):
                    st.write(f"{idx} ➜ {idx+1}: {d:.2f} km")
                st.markdown(f"**Total Distance:** {total_dist:.2f} km")

                # PyDeck visualization
                point_layer = pdk.Layer(
                    "ScatterplotLayer", df,
                    get_position='[lon, lat]', get_color='[255, 0, 0, 200]', get_radius=15000
                )
                path_data = pd.DataFrame({"path": [list(zip(df["lon"], df["lat"]))]})
                path_layer = pdk.Layer(
                    "PathLayer", path_data,
                    get_path="path", get_color=[0,128,255], get_width=4
                )
                view = pdk.ViewState(
                    latitude=df["lat"].mean(), longitude=df["lon"].mean(), zoom=5, pitch=0
                )
                deck = pdk.Deck(
                    map_style=None, map_provider="openstreetmap",
                    initial_view_state=view, layers=[path_layer, point_layer]
                )
                st.pydeck_chart(deck, use_container_width=True)

                # Save route to server
                if st.button("💾 Save Route to Server"):
                    save_res = requests.post("http://localhost:8000/save_route", json={"route": optimized})
                    if save_res.ok and save_res.json().get("status") == "saved":
                        st.success("✅ Route saved on server.")
                    else:
                        st.error("❌ Failed to save route.")

                # Download CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download CSV", csv,
                    file_name="optimized_route.csv", mime="text/csv"
                )

                # Download JSON
                json_bytes = json.dumps({"route": optimized}, indent=2).encode("utf-8")
                st.download_button(
                    "📥 Download JSON", json_bytes,
                    file_name="optimized_route.json", mime="application/json"
                )

    with col2:
        if st.button("🗑️ Clear All Locations"):
            st.session_state.all_locations.clear()
            st.info("All locations cleared.")
