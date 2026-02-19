"""
app.py
------
Streamlit dashboard interface for the mushroom forecasting planner.
Supports multiple independent production plans on one page.
"""

import pandas as pd
import streamlit as st
from datetime import date
from tables import MUSHROOMS, MUSHROOM_LIST, SUBSTRATE_TYPES, FRUITING_BAG_SIZES_LBS
from planner import compute_plan
from PIL import Image


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="Gulf Spore Workflow Forecasting Tool", layout="wide")

# Logo
try:
    logo = Image.open("images/GSHorizLogo.png")
    st.image(logo, width=350)
except:
    st.write("")  # if logo missing, ignore

st.title("Workflow Forecasting Tool")
st.caption("Plan one or more mushroom production schedules. Each plan has its own inputs and timeline.")

st.markdown("----")


# ---------------------------------------------------------
# HOW MANY PLANS?
# ---------------------------------------------------------
num_plans = st.number_input(
    "How many mushroom schedules do you want to plan?",
    min_value=1,
    max_value=5,
    value=1,
    step=1,
)

st.markdown("----")


# ---------------------------------------------------------
# LOOP OVER PLANS
# ---------------------------------------------------------
for i in range(num_plans):
    st.markdown(f"## Plan {i + 1}")

    # -----------------------------------------------------
    # INPUTS FOR THIS PLAN
    # -----------------------------------------------------
    top_cols = st.columns(4)
    with top_cols[0]:
        mush_name = st.selectbox(
            "Mushroom type",
            MUSHROOM_LIST,
            index=0,
            key=f"mush_type_{i}",
        )
    with top_cols[1]:
        desired_yield = st.number_input(
            "Desired yield (lbs)",
            min_value=0,
            value=100,
            step=5,
            key=f"desired_yield_{i}",
        )
    with top_cols[2]:
        desired_date = st.date_input(
            "Desired harvest date",
            value=date.today(),
            key=f"desired_date_{i}",
        )
    with top_cols[3]:
        bag_size = st.selectbox(
            "Fruiting bag size (lbs)",
            FRUITING_BAG_SIZES_LBS,
            index=0,
            key=f"bag_size_{i}",
        )

    mid_cols = st.columns(4)
    with mid_cols[0]:
        substrate_type = st.selectbox(
            "Substrate type",
            SUBSTRATE_TYPES,
            index=0,
            key=f"substrate_{i}",
        )
    with mid_cols[1]:
        spawn_purchased = st.toggle(
            "Spawn purchased? (Y/N)",
            value=True,
            key=f"spawn_{i}",
        )
    with mid_cols[2]:
        gsi_bag_size = st.selectbox(
            "Grain spawn bag size (lbs)",
            [3, 6],
            index=0,
            key=f"gsi_bag_{i}",
        )
    with mid_cols[3]:
        num_sterilizers = st.number_input(
            "# Sterilizers",
            min_value=1,
            value=2,
            step=1,
            key=f"num_sterilizers_{i}",
        )

    # -----------------------------------------------------
    # OPERATIONAL PARAMETERS (EXPANDER)
    # -----------------------------------------------------
    with st.expander("Operational parameters", expanded=False):
        op_cols = st.columns(4)
        with op_cols[0]:
            sub_bags_duration = st.number_input(
                "Substrate Bags: duration (days)",
                min_value=0.0,
                value=1.0,
                step=0.5,
                key=f"sub_bags_duration_{i}",
            )
        with op_cols[1]:
            sub_ster_duration = st.number_input(
                "Substrate Bag Sterilization: duration (days)",
                min_value=0.0,
                value=3.0,
                step=0.5,
                key=f"sub_ster_duration_{i}",
            )
        with op_cols[2]:
            gbs_duration = st.number_input(
                "Grain Bag Sterilization: duration (days)",
                min_value=0.0,
                value=1.0,
                step=0.5,
                key=f"gbs_duration_{i}",
            )

        with op_cols[3]:
            gbs_duration = st.number_input(
                "Fruiting: duration (days)",
                min_value=0.0,
                value=1.0,
                step=0.5,
                key=f"gbs_duration_{i}",
            )

    # -----------------------------------------------------
    # ONLY COMPUTE IF YIELD > 0
    # -----------------------------------------------------
    if desired_yield > 0:
        mush_row = MUSHROOMS[mush_name]

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
            gbs_duration_days=gbs_duration,
        )

        # -------------------------------------------------
        # DISPLAY RESULTS FOR THIS PLAN
        # -------------------------------------------------
        left, right = st.columns([1, 2])

        with left:
            st.subheader("Summary")
            st.metric("Fruiting bags", plan["summary"]["Fruiting bags"])

            start_dt = plan["summary"]["Schedule starts"]
            end_dt = plan["summary"]["Schedule ends"]

            st.metric("Schedule starts", start_dt.strftime("%Y-%m-%d"))
            st.metric("Schedule ends", end_dt.strftime("%Y-%m-%d"))
            st.metric("Total duration", plan["summary"]["Total duration"])

        with right:
            st.subheader("Workflow Timeline")
            df = pd.DataFrame(plan["blocks"])
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download schedule (CSV)",
                df.to_csv(index=False),
                f"schedule_plan_{i + 1}.csv",
                "text/csv",
                key=f"download_csv_{i}",
            )

        st.subheader("Mix Ratio (per bag)")
        mix_df = pd.DataFrame(plan["mix_ratio"])
        st.dataframe(mix_df, use_container_width=True)

        st.subheader("Materials (Total Quantities)")
        materials_df = pd.DataFrame(plan["materials"])
        st.dataframe(materials_df, use_container_width=True)

    else:
        st.info("Enter a positive desired yield to generate a schedule.")

    st.markdown("----")
