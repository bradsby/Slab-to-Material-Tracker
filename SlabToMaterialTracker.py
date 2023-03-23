import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SlabToMaterialTracker",
    page_icon='📍',
    layout="wide",
    initial_sidebar_state="expanded",
)

path_qa = st.sidebar.file_uploader(
    "QADataRaw2Polished",
    type="csv",
    accept_multiple_files=False,
)

path_equipment = st.sidebar.file_uploader(
    "Equipment Settings",
    type="csv",
    accept_multiple_files=False,
)

path_transactions = st.sidebar.file_uploader(
    "Transactions Details",
    type="csv",
    accept_multiple_files=False,
)

if path_qa:
    st.header("Slab Information")

    df_qa = pd.read_csv(
        path_qa,
        parse_dates=["SlabCreateDate"],
    )

    design_list = st.multiselect(
        "Design", df_qa["DESIGN"].unique(), default=df_qa["DESIGN"].unique()
    )
    df_qa = df_qa[df_qa["DESIGN"].isin(design_list)]

    thickness_list = st.multiselect(
        "Thickness", df_qa["TH"].unique(), default=df_qa["TH"].unique()
    )
    df_qa = df_qa[df_qa["TH"].isin(thickness_list)]

    fg_number_list = st.multiselect("Slab #", df_qa["FG #"].unique())
    df_qa = df_qa[df_qa["FG #"].isin(fg_number_list)]

    df_qa = df_qa[["TH", "DESIGN", "FG #", "SlabCreateDate"]].drop_duplicates()

    st.dataframe(df_qa)


if path_equipment:
    st.header("Mixer Information")

    df_equipment = pd.read_csv(
        path_equipment,
        parse_dates=["Record Timestamp"],
    )

    end_time = df_qa["SlabCreateDate"].values[0]
    start_time = end_time - np.timedelta64(6, "h")

    design = df_qa["DESIGN"].values[0]

    df_equipment = df_equipment[
        (
            (df_equipment["Record Timestamp"] >= start_time)
            & (df_equipment["Record Timestamp"] <= end_time)
            & (df_equipment["Design"] == design)
        )
    ]

    st.dataframe(df_equipment)

if path_transactions:
    st.header("Hopper Transactions")

    df_transactions = pd.read_csv(
        path_transactions,
        parse_dates=["Transaction Date"],
    )

    df_equipment["Record Timestamp"].max()

    end_mixer_time = df_equipment["Record Timestamp"].max()
    start_mixer_time = df_equipment["Record Timestamp"].min() - np.timedelta64(6, "h")

    raw_materials = df_equipment["DESCRIPTION"].unique().tolist()

    df_transactions = df_transactions[
        (
            (df_transactions["Transaction Date"] >= start_mixer_time)
            & (df_transactions["Transaction Date"] <= end_mixer_time)
            & (df_transactions["Item Description"].isin(raw_materials))
        )
    ]

    st.dataframe(df_transactions)

    @st.cache
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    csv = convert_df(df_transactions)

    st.download_button(
        label="Download 'Hopper Transactions' as CSV",
        data=csv,
        file_name="Hopper Transactions.csv",
        mime="text/csv",
    )
