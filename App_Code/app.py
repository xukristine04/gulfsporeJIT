"""
app.py
------
Streamlit dashboard interface for the mushroom forecasting planner.
Everything here uses simple Python — no type hints.
"""

import pandas as pd
import streamlit as st
from datetime import date
from tables import MUSHROOMS, MUSHROOM_LIST, SUBSTRATE_TYPES, FRUITING_BAG_SIZES_LBS
from planner import compute_plan
from PIL import Image

st.set_page_config(page_title="Gulf Spore Workflow Forecasting Tool", layout="wide")

# --- Display Gulf Spore Logo ---
# Load and display logo
logo = Image.open("images/GSHorizLogo.png")  # adjust path if needed
st.image(logo, use_column_width=False, width=350)  # width can be adjusted (250–400 works well)

# Add some vertical spacing after logo
st.markdown("<br>", unsafe_allow_html=True)



st.title("Workflow Forecasting Tool")

# --- Sidebar: user inputs ---
with st.sidebar:
    st.header("Desired Outputs")
    desired_yield = st.number_input("Desired yield (lbs)", min_value=0, value=100, step=5)
    desired_date = st.date_input("Desired harvest date", value=date.today())
    bag_size = st.selectbox("Fruiting bag size (lbs)", FRUITING_BAG_SIZES_LBS, index=0)
    mush_name = st.selectbox("Mushroom type", MUSHROOM_LIST, index=0)
    substrate_type = st.selectbox("Substrate type", SUBSTRATE_TYPES, index=0)
    spawn_purchased = st.toggle("Spawn purchased? (Y/N)", value=True)

    st.divider()
    st.caption("Operational parameters")
    sub_bags_duration = st.number_input("Substrate Bags: duration (days)", min_value=0.0, value=1.0, step=0.5)
    sub_ster_duration = st.number_input("Substrate Bag Sterilization: duration (days)", min_value=0.0, value=3.0, step=0.5)
    num_sterilizers = st.number_input("# Sterilizers", min_value=1, value=2, step=1)
    gsi_bag_size = st.selectbox("Grain spawn bag size (lbs)", [3, 6], index=0)
    gbs_duration = st.number_input("Grain Bag Sterilization: duration (days)", min_value=0.0, value=1.0, step=0.5)

# Get selected mushroom’s data from tables.py
mush_row = MUSHROOMS[mush_name]

# Run calculations
plan = compute_plan(
    desired_yield_lbs=desired_yield,
    desired_harvest_date=desired_date,
    fruiting_bag_size_lbs=bag_size,
    mushroom_row=mush_row,
    substrate_type=substrate_type,
    spawn_purchased=spawn_purchased,
    sub_bags_duration_days=sub_bags_duration,
    sub_ster_duration_days=sub_ster_duration,
    num_sterilizers=num_sterilizers,
    gsi_bag_size_lbs=gsi_bag_size,
    gbs_duration_days=gbs_duration
)

# --- Display results ---
left, right = st.columns([1, 2])

with left:
    st.subheader("Summary")
    st.metric("Fruiting bags", plan["summary"]["Fruiting bags"])

    # Convert the datetime.date into a readable string for Streamlit
    start_dt = plan["summary"]["Schedule starts"]
    end_dt = plan["summary"]["Schedule ends"]

    # st.metric only accepts int, float, str, or None — so we use strftime() to format dates
    st.metric("Schedule starts", start_dt.strftime("%Y-%m-%d"))
    st.metric("Schedule ends", end_dt.strftime("%Y-%m-%d"))
    st.metric("Total duration", plan["summary"]["Total duration"])

with right:
    st.subheader("Workflow Timeline")
    df = pd.DataFrame(plan["blocks"])
    st.dataframe(df, use_container_width=True)
    st.download_button("Download schedule (CSV)", df.to_csv(index=False), "schedule.csv", "text/csv")

st.divider()
# --- MIX RATIO TABLE ---
st.subheader("Mix Ratio (per bag)")
mix_df = pd.DataFrame(plan["mix_ratio"])
st.dataframe(mix_df, use_container_width=True)

# --- MATERIAL TOTALS TABLE ---
st.subheader("Materials (Total Quantities)")
materials_df = pd.DataFrame(plan["materials"])
st.dataframe(materials_df, use_container_width=True)
