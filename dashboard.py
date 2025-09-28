import streamlit as st
import pandas as pd
from supabase import create_client

# -------------------------------
# 1. Supabase Setup
# -------------------------------
url = "https://zpfjuktjmabbrovcpypu.supabase.co"   # Replace with your Supabase project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwZmp1a3RqbWFiYnJvdmNweXB1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkwNzgxNjAsImV4cCI6MjA3NDY1NDE2MH0.sSHWN8no6loVuhu7UYXwZ9tFUXNiYG4v6kMuRbs-9vk"                     # Replace with your Supabase service role key
supabase = create_client(url, key)

# -------------------------------
# 2. Fetch Data from Supabase
# -------------------------------
response = supabase.table("spotify_tracks").select("*").execute()
data = response.data
df = pd.DataFrame(data)

st.title("🎵 Spotify Data Analytics Dashboard")
st.markdown("Built with **Streamlit + Supabase + Spotify API**")

if df.empty:
    st.warning("No data found in the database. Run the ETL script first.")
else:
    # -------------------------------
    # 3. Show Raw Data
    # -------------------------------
    st.subheader("Raw Data (Latest 10 Records)")
    st.dataframe(df.tail(10))

    # -------------------------------
    # 4. Top Tracks by Popularity
    # -------------------------------
    st.subheader("🔥 Top 5 Tracks by Popularity")
    top_tracks = df.sort_values("popularity", ascending=False).head(5)
    st.bar_chart(top_tracks.set_index("track_name")["popularity"])

    # -------------------------------
    # 5. Popularity Category Distribution
    # -------------------------------
    st.subheader("📊 Popularity Category Distribution")
    pop_dist = df["popularity_category"].value_counts()
    st.bar_chart(pop_dist)

    # -------------------------------
    # 6. Duration Category Distribution
    # -------------------------------
    st.subheader("⏱️ Duration Category Distribution")
    dur_dist = df["duration_category"].value_counts()
    st.bar_chart(dur_dist)

    # -------------------------------
    # 7. Average Track Duration per Artist (Top 5)
    # -------------------------------
    st.subheader("🎤 Top 5 Artists by Average Track Duration")
    avg_duration = df.groupby("artist")["duration_minutes"].mean().sort_values(ascending=False).head(5)
    st.bar_chart(avg_duration)
