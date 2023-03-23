import numpy as np
import pandas as pd
import streamlit as st


def format_headers(df):
    df.columns = df.columns.str.replace(" ", "_").str.upper()
    return df


st.set_page_config(
    page_title="SlabToMaterialTracker",
    page_icon="📍",
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

    df_qa = format_headers(
        pd.read_csv(
            path_qa,
            parse_dates=["SLABCREATEDATE"],
        )
    )

    design_list = st.multiselect(
        "Design", df_qa["DESIGN"].unique(), default=df_qa["DESIGN"].unique()
    )
    df_qa = df_qa.query("DESIGN.isin(@design_list")

    thickness_list = st.multiselect(
        "Thickness", df_qa["TH"].unique(), default=df_qa["TH"].unique()
    )
    df_qa = df_qa.query("TH.isin(@thickness_list")

    fg_number_list = st.multiselect("Slab #", df_qa["FG_#"].unique())
    df_qa = df_qa[df_qa["FG_#"].isin(fg_number_list)]

    df_qa = df_qa[["TH", "DESIGN", "FG_#", "SLABCREATEDATE"]].drop_duplicates()

    st.dataframe(df_qa)


if path_equipment:
    st.header("Mixer Information")

    df_equipment = format_headers(
        pd.read_csv(
            path_equipment,
            parse_dates=["RECORD_TIMESTAMP"],
        )
    )

    end_time = df_qa["SLABCREATEDATE"].values[0]
    start_time = end_time - np.timedelta64(6, "h")

    design = df_qa["DESIGN"].values[0]

    df_equipment = df_equipment.query(
        "DESIGN==@design and @start_time <= RECORD_TIMESTAMP <= @end_time"
    )
    st.dataframe(df_equipment)

if path_transactions:
    st.header("Hopper Transactions")

    df_transactions = format_headers(
        pd.read_csv(
            path_transactions,
            parse_dates=["TRANSACTION_DATE"],
        )
    )

    df_equipment["RECORD_TIMESTAMP"].max()

    end_mixer_time = df_equipment["RECORD_TIMESTAMP"].max()
    start_mixer_time = df_equipment["RECORD_TIMESTAMP"].min() - np.timedelta64(6, "h")

    raw_materials_list = st.multiselect(
        "Raw Materials", df_qa["ITEM_DESCRIPTION"].unique()
    )

    df_transactions = df_transactions.query(
        "ITEM_DESCRIPTION.isin(@design) and @start_mixer_time <= TRANSACTION_DATE <= @end_mixer_time"
    )

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
