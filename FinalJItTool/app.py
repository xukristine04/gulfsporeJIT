"""
app.py
------
Streamlit dashboard interface for the mushroom forecasting planner.
Multi-plan builder + master schedule Gantt view.
"""

import pandas as pd
import streamlit as st
from datetime import date
from tables import MUSHROOMS, MUSHROOM_LIST, SUBSTRATE_TYPES, FRUITING_BAG_SIZES_LBS
from planner import compute_plan
from PIL import Image
import plotly.express as px

# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Gulf Spore Workflow Forecasting Tool",
    layout="wide",
)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "custom_mushrooms" not in st.session_state:
    st.session_state.custom_mushrooms = {}

if "show_new_species_form" not in st.session_state:
    st.session_state.show_new_species_form = False

# ---------------------------------------------------------
# HEADER / LOGO
# ---------------------------------------------------------
try:
    logo = Image.open("images/GSHorizLogo.png")
    st.image(logo, width=350)
except Exception:
    # If logo missing just skip
    pass

st.title("Workflow Forecasting Tool")
st.caption(
    "Build one or more mushroom production schedules, then view a consolidated master timeline."
)

# Tabs: Plan Builder + Master Schedule
tab_builder, tab_master = st.tabs(["Plan Builder", "Master Schedule"])

# This will collect all blocks from all plans for the master schedule
master_rows = []

# ---------------------------------------------------------
# TAB 1: PLAN BUILDER
# ---------------------------------------------------------
with tab_builder:
    # --- TOP-OF-PAGE NEW SPECIES FORM --------------------
    if st.session_state.show_new_species_form:
        st.subheader("➕ Create New Mushroom Species")

        with st.form("new_species_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_species_name = st.text_input(
                    "Species Name*",
                    placeholder="e.g., Golden Oyster",
                )
                new_incubation_days = st.number_input(
                    "Incubation Days*",
                    min_value=1,
                    value=14,
                    step=1,
                )
                new_cultural_inoculation_days = st.number_input(
                    "Cultural Inoculation Days*",
                    min_value=1,
                    value=21,
                    step=1,
                )

            with col2:
                new_fruiting_days = st.number_input(
                    "Fruiting Days*",
                    min_value=1,
                    value=14,
                    step=1,
                )
                new_expected_yield_ratio = st.number_input(
                    "Expected yield ratio (lb mushrooms per lb substrate)*",
                    min_value=0.01,
                    max_value=1.0,
                    value=0.20,
                    step=0.01,
                    format="%.2f",
                )
                new_default_grain_size = st.selectbox(
                    "Default Grain Size (lbs)*",
                    [3, 6],
                    index=0,
                )

            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit_button = st.form_submit_button(
                    "✓ Create Species",
                    use_container_width=True,
                )
            with col_cancel:
                cancel_button = st.form_submit_button(
                    "✗ Cancel",
                    use_container_width=True,
                )

            if submit_button:
                if new_species_name.strip() == "":
                    st.error("Please enter a species name.")
                else:
                    # Check against default + existing custom
                    all_mushrooms_check = {
                        **MUSHROOMS,
                        **st.session_state.custom_mushrooms,
                    }
                    if new_species_name in all_mushrooms_check:
                        st.error(
                            f"Species '{new_species_name}' already exists. "
                            "Please use a different name."
                        )
                    else:
                        st.session_state.custom_mushrooms[new_species_name] = {
                            "incubation_days": new_incubation_days,
                            "cultural_inoculation_days": new_cultural_inoculation_days,
                            "fruiting_days": new_fruiting_days,
                            "expected_yield_ratio": new_expected_yield_ratio,
                            "default_grain_size_lbs": new_default_grain_size,
                        }
                        st.session_state.show_new_species_form = False
                        st.success(
                            f"✓ Species '{new_species_name}' created successfully!"
                        )
                        st.rerun()

            if cancel_button:
                st.session_state.show_new_species_form = False
                st.rerun()

        st.markdown("---")

    # --- COMBINED MUSHROOM LIST --------------------------
    all_mushrooms = {**MUSHROOMS, **st.session_state.custom_mushrooms}
    all_mushroom_list = list(all_mushrooms.keys()) + ["+New species"]

    # --- NUMBER OF PLANS ---------------------------------
    num_plans = st.number_input(
        "How many mushroom schedules do you want to plan?",
        min_value=1,
        max_value=5,
        value=1,
        step=1,
    )

    st.markdown("---")

    # --- LOOP OVER PLANS ---------------------------------
    for i in range(num_plans):
        st.markdown(f"### Plan {i + 1}")

        # ---------- CORE INPUTS ----------
        top_cols = st.columns(4)
        with top_cols[0]:
            mush_name = st.selectbox(
                "Mushroom type",
                all_mushroom_list,
                index=0,
                key=f"mush_type_{i}",
            )

            # If a custom species is selected, allow delete
            if mush_name in st.session_state.custom_mushrooms:
                if st.button(
                    "🗑️ Delete this species",
                    key=f"delete_species_{i}",
                    use_container_width=True,
                ):
                    del st.session_state.custom_mushrooms[mush_name]
                    st.success(f"Deleted '{mush_name}' successfully!")
                    st.rerun()

            # Handle +New species
            if mush_name == "+New species":
                st.session_state.show_new_species_form = True
                # Use first default for calc until new species exists
                mush_name_for_calc = MUSHROOM_LIST[0]
            else:
                mush_name_for_calc = mush_name

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

        # Operational parameters
        with st.expander("Operational parameters", expanded=True):
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
                fruiting_duration = st.number_input(
                    "Fruiting: duration (days)",
                    min_value=0.0,
                    value=1.0,
                    step=0.5,
                    key=f"fruiting_duration_{i}",
                )


        # ---------- RUN THIS PLAN ----------
        if desired_yield > 0:
            mush_row = all_mushrooms[mush_name_for_calc]
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

            # ----- Per-plan outputs -----
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
                st.subheader("Workflow Timeline (this plan only)")
                df_blocks = pd.DataFrame(plan["blocks"])
                st.dataframe(df_blocks, use_container_width=True)
                st.download_button(
                    "Download schedule (CSV)",
                    df_blocks.to_csv(index=False),
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

            # ----- Feed into master schedule -----
            for block in plan["blocks"]:
                master_rows.append(
                    {
                        "Plan": i + 1,
                        "Mushroom": mush_name_for_calc,
                        "Task": block["name"],
                        "Start": block["date_start"],
                        "End": block["date_end"],
                        "Duration (days)": block["duration_days"],
                        "Desired Yield (lbs)": desired_yield,
                    }
                )
        else:
            st.info("Enter a positive desired yield to generate a schedule.")

        st.markdown("---")

# ---------------------------------------------------------
# TAB 2: MASTER SCHEDULE (GANTT)
# ---------------------------------------------------------
with tab_master:
    st.subheader("Consolidated Master Schedule")

    if not master_rows:
        st.info(
            "Build at least one plan in the **Plan Builder** tab to see the master schedule."
        )
    else:
        df_master = pd.DataFrame(master_rows)

        # Gantt-style timeline across all plans
        fig = px.timeline(
            df_master,
            x_start="Start",
            x_end="End",
            y="Mushroom",   # you can change to "Plan" or combine them later
            color="Task",
            hover_data=["Plan", "Desired Yield (lbs)"],
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            margin=dict(l=30, r=30, t=30, b=30),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Master Schedule Table")
        st.dataframe(df_master, use_container_width=True)


