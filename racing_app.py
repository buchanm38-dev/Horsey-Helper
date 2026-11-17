python
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Daily Racing Matcher", layout="wide")
st.title("Daily Racing System Matcher")
st.caption("Scans the card and flags horses that match the progressive + strong yard + tactical style system")

# Sample data so you can test immediately
sample_data = {
    "Race": ["Goodwood 14:25", "Goodwood 14:25", "York 15:00", "York 15:00", "Newbury 16:10"],
    "Horse": ["Drumbeat", "Capability Brown", "Progressive Type", "Firm Only", "Class Dropper"],
    "Age": [2, 2, 3, 4, 4],
    "Trainer": ["Aidan O'Brien", "Aidan O'Brien", "William Haggas", "Unknown", "Andrew Balding"],
    "LastTwo": ["1-1", "2-1", "1-3", "4-5", "1-2"],
    "Style": ["mid-pack", "tactical", "prominent", "front", "mid-pack"],
    "SoftForm": ["Yes", "Yes", "Yes", "No", "Yes"],
    "ClassDrop": ["No", "No", "Yes", "No", "Yes"],
    "CourseFit": ["Yes", "Yes", "Yes", "No", "Yes"],
    "Notes": ["Progressive 2yo", "Improving", "Strong yard", "Firm only", "Mark drop"]
}

uploaded_file = st.file_uploader("Upload today's runners CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("No file uploaded — using sample data so you can see how it works.")
    df = pd.DataFrame(sample_data)

# Strong yards list (from your system)
strong_yards = ["haggas", "balding", "o'brien", "obrien", "aidan", "burke", "gosden", "scott"]

def score_horse(row):
    score = 0
    reasons = []

    # Progressive last-two
    lt = str(row.get("LastTwo", "")).lower()
    if any(x in lt for x in ["1-", "2-1", "1-1", "1-2", "2-1"]):
        score += 30
        reasons.append("Progressive last-two")

    # Strong yard
    trainer = str(row.get("Trainer", "")).lower()
    if any(y in trainer for y in strong_yards):
        score += 25
        reasons.append("Strong yard")

    # Style preference
    style = str(row.get("Style", "")).lower()
    if "mid" in style or "tactical" in style or "handy" in style:
        score += 20
        reasons.append("Tactical/mid-pack style")
    elif "front" in style:
        score -= 10
        reasons.append("Pure front-runner (weaker fit)")

    # Soft / GTS form
    soft = str(row.get("SoftForm", "")).lower()
    if soft in ["yes", "y", "true", "1"]:
        score += 15
        reasons.append("Soft/GTS form")

    # Class/mark drop
    if str(row.get("ClassDrop", "")).lower() in ["yes", "y"]:
        score += 15
        reasons.append("Class/mark drop")

    # Course fit
    if str(row.get("CourseFit", "")).lower() in ["yes", "y"]:
        score += 10
        reasons.append("Course/similar track fit")

    # Age caution for raw 2yos
    try:
        age = int(row.get("Age", 0))
        if age == 2 and "1-" not in lt:
            score -= 15
            reasons.append("Raw 2yo caution")
    except:
        pass

    return score, "; ".join(reasons) if reasons else "Weak match"

# Apply scoring
df["Score"], df["Match Reasons"] = zip(*df.apply(score_horse, axis=1))
df = df.sort_values("Score", ascending=False)

# Display
st.subheader("Daily Matches (highest score first)")
st.dataframe(
    df[["Race", "Horse", "Trainer", "Score", "Match Reasons", "LastTwo", "Style"]],
    use_container_width=True,
    hide_index=True
)

strong = df[df["Score"] >= 50]
