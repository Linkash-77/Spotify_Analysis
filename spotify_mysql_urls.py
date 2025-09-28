from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
from supabase import create_client

# -------------------------------
# 1. Spotify API Setup
# -------------------------------
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="be5dff7d0fe44a74a0e2309b22c9e770",  
    client_secret="4094e27c4fce4f67bfaba89ce6290ae5" 
))

# -------------------------------
# 2. Supabase Setup
# -------------------------------
url = "https://zpfjuktjmabbrovcpypu.supabase.co"   
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwZmp1a3RqbWFiYnJvdmNweXB1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkwNzgxNjAsImV4cCI6MjA3NDY1NDE2MH0.sSHWN8no6loVuhu7UYXwZ9tFUXNiYG4v6kMuRbs-9vk"                      # Replace with your Supabase service role key
supabase = create_client(url, key)

# -------------------------------
# 3. Read Track URLs
# -------------------------------
file_path = "track_urls.txt"
with open(file_path, "r") as file:
    track_urls = [line.strip() for line in file.readlines()]

all_tracks = []

# -------------------------------
# 4. Process Each Track
# -------------------------------
for track_url in track_urls:
    try:
        track_id = re.search(r"track/([a-zA-Z0-9]+)", track_url).group(1)

        track = sp.track(track_id)

        # Transform step: add categories
        popularity = track["popularity"]
        duration = track["duration_ms"] / 60000

        popularity_category = "High" if popularity > 70 else "Medium" if popularity > 40 else "Low"
        duration_category = "Short" if duration < 3 else "Medium" if duration < 5 else "Long"

        track_data = {
            "track_id": track["id"],
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "popularity": popularity,
            "duration_minutes": duration,
            "popularity_category": popularity_category,
            "duration_category": duration_category,
            "inserted_at": datetime.utcnow().isoformat()
        }

        all_tracks.append(track_data)

        # Load into Supabase (incremental check)
        existing = supabase.table("spotify_tracks").select("id").eq("track_id", track["id"]).execute()

        if len(existing.data) == 0:
            supabase.table("spotify_tracks").insert(track_data).execute()
            print(f"Inserted: {track_data['track_name']} by {track_data['artist']}")
        else:
            print(f"Skipped duplicate: {track_data['track_name']}")

    except Exception as e:
        print(f"Error processing {track_url}: {e}")

# -------------------------------
# 5. Save to CSV
# -------------------------------
df = pd.DataFrame(all_tracks)
print("\nAll Tracks Data:")
print(df.head())

df.to_csv("spotify_tracks_data.csv", index=False)
print("\nData saved to spotify_tracks_data.csv")

# -------------------------------
# 6. Visualizations
# -------------------------------

# Popularity distribution
plt.figure(figsize=(8, 5))
plt.hist(df["popularity"], bins=10, color="skyblue", edgecolor="black")
plt.title("Track Popularity Distribution")
plt.xlabel("Popularity")
plt.ylabel("Count")
plt.show()

# Average duration per artist (top 5)
avg_duration = df.groupby("artist")["duration_minutes"].mean().sort_values(ascending=False).head(5)
plt.figure(figsize=(8, 5))
avg_duration.plot(kind="bar", color="lightgreen", edgecolor="black")
plt.title("Top 5 Artists by Average Track Duration")
plt.ylabel("Avg Duration (minutes)")
plt.show()

# Top 5 most popular tracks
top_tracks = df.sort_values("popularity", ascending=False).head(5)
plt.figure(figsize=(8, 5))
plt.barh(top_tracks["track_name"], top_tracks["popularity"], color="salmon", edgecolor="black")
plt.title("Top 5 Tracks by Popularity")
plt.xlabel("Popularity")
plt.gca().invert_yaxis()
plt.show()
