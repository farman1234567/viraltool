import streamlit as st
import requests
from datetime import datetime, timedelta

# ========================
# YOUTUBE API CONFIG
# ========================
API_KEY = "AIzaSyDiTQuy87y097i6Ya7M8joNSH4hKyM2-dU"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"

# ========================
# STREAMLIT UI
# ========================
st.set_page_config(page_title="Echoes of Napoleon – Viral History Finder", layout="wide")
st.title("🏛️ Echoes of Napoleon – Viral History Topics Finder")

days = st.number_input("Search videos from last X days", min_value=1, max_value=30, value=7)
min_views = st.number_input("Minimum views to qualify as viral", value=10000, step=1000)
max_subs = st.number_input("Maximum channel subscribers", value=3000, step=500)

# ========================
# HISTORY NICHE KEYWORDS
# ========================
keywords = [
    "Napoleonic Wars",
    "Napoleon Bonaparte Documentary",
    "Peninsular War",
    "Battle of Waterloo Explained",
    "Why Napoleon Failed",
    "French Revolution Documentary",
    "Forgotten Battles in History",
    "Empires That Collapsed",
    "Military History Documentary",
    "Greatest Generals in History",
    "Ancient Warfare Explained",
    "History That Changed the World",
    "War That Changed Europe",
    "Lost Empires Explained"
]

# ========================
# HELPER FUNCTION
# ========================
def yt_get(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# ========================
# MAIN LOGIC
# ========================
if st.button("🔥 Find Viral History Videos"):
    start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
    results = []

    for keyword in keywords:
        st.write(f"🔍 Searching: **{keyword}**")

        search_params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "order": "viewCount",
            "publishedAfter": start_date,
            "maxResults": 15,
            "key": API_KEY
        }

        search_data = yt_get(SEARCH_URL, search_params)

        if "items" not in search_data:
            continue

        videos = search_data["items"]

        video_ids = [v["id"]["videoId"] for v in videos]
        channel_ids = list(set(v["snippet"]["channelId"] for v in videos))

        # VIDEO STATS
        video_stats = yt_get(VIDEOS_URL, {
            "part": "statistics",
            "id": ",".join(video_ids),
            "key": API_KEY
        })

        video_views = {
            v["id"]: int(v["statistics"].get("viewCount", 0))
            for v in video_stats.get("items", [])
        }

        # CHANNEL STATS
        channel_stats = yt_get(CHANNELS_URL, {
            "part": "statistics",
            "id": ",".join(channel_ids),
            "key": API_KEY
        })

        channel_subs = {
            c["id"]: int(c["statistics"].get("subscriberCount", 0))
            for c in channel_stats.get("items", [])
        }

        # MERGE DATA SAFELY
        for v in videos:
            vid = v["id"]["videoId"]
            cid = v["snippet"]["channelId"]

            views = video_views.get(vid, 0)
            subs = channel_subs.get(cid, 0)

            if views >= min_views and subs <= max_subs:
                results.append({
                    "title": v["snippet"]["title"],
                    "desc": v["snippet"]["description"][:160],
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "views": views,
                    "subs": subs,
                    "keyword": keyword
                })

    # ========================
    # OUTPUT RESULTS
    # ========================
    if results:
        st.success(f"🔥 Found {len(results)} viral history opportunities!")

        results = sorted(results, key=lambda x: x["views"], reverse=True)

        for r in results:
            st.markdown(
                f"""
### 📜 {r['title']}
**Keyword Trigger:** {r['keyword']}  
👁️ Views: **{r['views']:,}**  
👥 Channel Subs: **{r['subs']:,}**  
🔗 [Watch Video]({r['url']})
---
"""
            )
    else:
        st.warning("No viral history videos found under current filters.")
