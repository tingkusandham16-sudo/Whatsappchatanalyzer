import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="centered"
)

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 WhatsApp Chat Analyzer")
st.caption("Privacy-safe • No data stored • Perfect for Reels & Memes")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📂 Upload WhatsApp chat (.txt, without media)",
    type="txt"
)

# ---------------- FUNCTIONS ----------------
def extract_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(text)

# ---------------- MAIN LOGIC ----------------
if uploaded_file:
    raw_data = uploaded_file.read().decode("utf-8")

    messages = []
    for line in raw_data.split("\n"):
        if " - " in line:
            try:
                date_time, msg = line.split(" - ", 1)
                date, time = date_time.split(", ")
                sender, message = msg.split(": ", 1)
                messages.append([date, time, sender, message])
            except:
                pass

    df = pd.DataFrame(
        messages,
        columns=["Date", "Time", "Sender", "Message"]
    )

    if df.empty:
        st.error("❌ Could not read chat file.")
        st.stop()

    st.success("✅ Chat loaded successfully")

    # ---------------- BASIC CLEANING ----------------
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.hour

    # ---------------- WHATSAPP WRAPPED ----------------
    st.header("🎁 WhatsApp Wrapped")

    col1, col2, col3 = st.columns(3)
    col1.metric("💬 Total Messages", len(df))
    col2.metric("👥 Total Users", df["Sender"].nunique())
    col3.metric("🏆 Top Sender", df["Sender"].value_counts().idxmax())

    night_msgs = df[df["Hour"] >= 22]
    st.metric("🌙 Night Messages (after 10 PM)", len(night_msgs))

    # ---------------- MESSAGE COUNT CHART ----------------
    st.header("📊 Messages per Person")

    msg_count = df["Sender"].value_counts()

    fig1, ax1 = plt.subplots()
    msg_count.plot(kind="bar", ax=ax1)
    ax1.set_ylabel("Messages")
    ax1.set_xlabel("Person")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("messages_per_person.png")
    st.pyplot(fig1)

    with open("messages_per_person.png", "rb") as f:
        st.download_button(
            "📸 Download Chart",
            f,
            file_name="messages_per_person.png",
            mime="image/png"
        )

    # ---------------- EMOJI ANALYZER ----------------
    st.header("😂 Emoji Analyzer")

    all_emojis = []
    for msg in df["Message"]:
        all_emojis.extend(extract_emojis(msg))

    if all_emojis:
        emoji_counter = Counter(all_emojis)
        emoji_df = pd.DataFrame(
            emoji_counter.most_common(10),
            columns=["Emoji", "Count"]
        )

        fig2, ax2 = plt.subplots()
        ax2.bar(emoji_df["Emoji"], emoji_df["Count"])
        ax2.set_ylabel("Count")
        plt.tight_layout()

        plt.savefig("emoji_stats.png")
        st.pyplot(fig2)

        with open("emoji_stats.png", "rb") as f:
            st.download_button(
                "📸 Download Emoji Chart",
                f,
                file_name="emoji_stats.png",
                mime="image/png"
            )
    else:
        st.info("No emojis found in this chat.")

    # ---------------- ACTIVITY BY HOUR ----------------
    st.header("⏰ Activity by Hour")

    hour_count = df["Hour"].value_counts().sort_index()

    fig3, ax3 = plt.subplots()
    ax3.plot(hour_count.index, hour_count.values, marker="o")
    ax3.set_xlabel("Hour of Day")
    ax3.set_ylabel("Messages")
    plt.tight_layout()

    plt.savefig("activity_by_hour.png")
    st.pyplot(fig3)

    with open("activity_by_hour.png", "rb") as f:
        st.download_button(
            "📸 Download Hour Chart",
            f,
            file_name="activity_by_hour.png",
            mime="image/png"
        )

    st.success("🚀 Ready for screenshots, reels & memes!")
