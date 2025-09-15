import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os
import re
from urllib.parse import urlparse, parse_qs

def get_openai_api_key():
    # Try streamlit secrets, then environment variable
    return st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

openai.api_key = get_openai_api_key()

def extract_youtube_id(youtube_url):
    """
    Robust extraction of YouTube video ID from various URL formats.
    """
    # Handle standard YouTube URL with v=
    match = re.search(r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/)([A-Za-z0-9_-]{11})", youtube_url)
    if match:
        return match.group(1)
    # Fallback to urlparse
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        qs = parse_qs(parsed_url.query)
        return qs.get("v", [""])[0]
    return ""

def get_transcript(youtube_url):
    video_id = extract_youtube_id(youtube_url)
    if not video_id or len(video_id) != 11:
        return "❌ Error: Could not extract valid YouTube video ID."
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return " ".join([t['text'] for t in transcript])
    except Exception as e:
        return f"❌ Error fetching transcript: {e}"

def repurpose_content(transcript, style="blog post"):
    prompt = f"Turn this transcript into a {style}:\n\n{transcript}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error generating content: {e}"

st.set_page_config(page_title="AI Content Repurposer", page_icon="🎥", layout="wide")
st.title("🎥 AI Content Repurposer")
st.write("Paste a YouTube link and turn it into a Blog Post, LinkedIn Post, and Tweet Thread — instantly!")

youtube_url = st.text_input("Enter YouTube URL:")

if st.button("Generate"):
    if youtube_url.strip() == "":
        st.error("⚠️ Please enter a valid YouTube URL")
    else:
        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(youtube_url)

        if transcript.startswith("❌"):
            st.error(transcript)
        else:
            st.subheader("📝 Transcript")
            st.write(transcript)

            with st.spinner("Repurposing with AI..."):
                blog = repurpose_content(transcript, "blog post")
                linkedin = repurpose_content(transcript, "LinkedIn post")
                tweet = repurpose_content(transcript, "tweet thread")

            st.subheader("📖 Blog Post")
            st.write(blog)

            st.subheader("💼 LinkedIn Post")
            st.write(linkedin)

            st.subheader("🐦 Tweet Thread")
            st.write(tweet)

            st.success("✅ Content generated successfully!")
