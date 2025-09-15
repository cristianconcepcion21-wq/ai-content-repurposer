import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os

def get_transcript(youtube_url):
    try:
        video_id = youtube_url.split("v=")[1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return " ".join([t['text'] for t in transcript])
    except Exception as e:
        return f"❌ Error fetching transcript: {e}"

def repurpose_content(transcript, style="blog post"):
    prompt = f"Turn this transcript into a {style}:\n\n{transcript}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

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
