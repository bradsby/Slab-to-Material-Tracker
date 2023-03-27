import numpy as np
import pandas as pd
import streamlit as st


def format_headers(df):
    df.columns = df.columns.str.replace(" ", "_").str.upper()
    return df


st.set_page_config(
    page_title="SlabToMaterialTracker",
    page_icon="📍",
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
            parse_dates=["SlabCreateDate"],
        )
    )

    df_qa = df_qa.rename(columns={"FG_#": "FG_Number"})
    
    design_list = st.multiselect(
        "Design", df_qa["DESIGN"].unique(), default=df_qa["DESIGN"].unique()
    )
    df_qa = df_qa.query("DESIGN==@design_list")

    thickness_list = st.multiselect(
        "Thickness", df_qa["TH"].unique(), default=df_qa["TH"].unique()
    )
    df_qa = df_qa.query("TH==@thickness_list")

    fg_number_list = st.multiselect("Slab #", df_qa["FG_Number"].unique())
    df_qa = df_qa.query("FG_Number==@fg_number_list")

    df_qa = df_qa[["TH", "DESIGN", "FG_Number", "SLABCREATEDATE"]].drop_duplicates()

    try:
        st.dataframe(df_qa)
    except pd.errors.UndefinedVariableError:
        st.warning("Choose slab number(s).")



if path_equipment:
    st.header("Mixer Information")

    df_equipment = format_headers(
        pd.read_csv(
            path_equipment,
            parse_dates=["Record Timestamp"],
        )
    )

    end_time = df_qa["SLABCREATEDATE"].values[0]
    start_time = end_time - np.timedelta64(6, "h")

    design = df_qa["DESIGN"].values[0]

    df_equipment = df_equipment.query(
        "DESIGN==@design and @start_time <= RECORD_TIMESTAMP <= @end_time"
    )
    st.dataframe(df_equipment, use_container_width=True)

if path_transactions:
    st.header("Hopper Transactions")

    df_transactions = format_headers(
        pd.read_csv(
            path_transactions,
            parse_dates=["Transaction Date"],
        )
    )

    df_equipment["RECORD_TIMESTAMP"].max()

    end_mixer_time = df_equipment["RECORD_TIMESTAMP"].max()
    start_mixer_time = df_equipment["RECORD_TIMESTAMP"].min() - np.timedelta64(6, "h")

    raw_materials_list = st.multiselect(
        "Raw Materials", sorted(df_transactions["ITEM_DESCRIPTION"].unique())
    )

    df_transactions = df_transactions.query(
        "ITEM_DESCRIPTION==@raw_materials_list and @start_mixer_time <= TRANSACTION_DATE <= @end_mixer_time"
    )

    st.dataframe(df_transactions, use_container_width=True)

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    csv = convert_df(df_transactions)

    st.download_button(
        label="Download 'Hopper Transactions' as CSV",
        data=csv,
        file_name="Hopper Transactions.csv",
        mime="text/csv",
    )
