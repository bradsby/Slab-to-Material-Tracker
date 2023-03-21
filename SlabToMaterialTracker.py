import numpy as np
import pandas as pd
import streamlit as st

st.header("Tableau Reports")

path1 = st.file_uploader(
    "QADataRaw2Polished",
    type="csv",
    accept_multiple_files=False,
)

path2 = st.file_uploader(
    "Equipment Settings",
    type="csv",
    accept_multiple_files=False,
)

path3 = st.file_uploader(
    "Transactions Details",
    type="csv",
    accept_multiple_files=False,
)

if path1:
    st.header("Slab Information")

    df1 = pd.read_csv(
        path1,
        parse_dates=["SlabCreateDate"],
    )

    design_list = st.sidebar.multiselect(
        "Design", df1["DESIGN"].unique(), default=df1["DESIGN"].unique()
    )
    df1 = df1[df1["DESIGN"].isin(design_list)]

    thickness_list = st.sidebar.multiselect(
        "Thickness", df1["TH"].unique(), default=df1["TH"].unique()
    )
    df1 = df1[df1["TH"].isin(thickness_list)]

    fg_number_list = st.sidebar.multiselect("Slab #", df1["FG #"].unique())
    df1 = df1[df1["FG #"].isin(fg_number_list)]

    df1 = df1[["TH", "DESIGN", "FG #", "SlabCreateDate"]].drop_duplicates()

    st.dataframe(df1)


if path2:
    st.header("Mixer Information")

    df2 = pd.read_csv(
        path2,
        parse_dates=["Record Timestamp"],
    )

    end_time = df1["SlabCreateDate"].values[0]
    start_time = end_time - np.timedelta64(6, "h")

    design = df1["DESIGN"].values[0]

    df2 = df2[
        (
            (df2["Record Timestamp"] >= start_time)
            & (df2["Record Timestamp"] <= end_time)
            & (df2["Design"] == design)
        )
    ]

    st.dataframe(df2)

if path3:
    st.header("Hopper Transactions")

    df3 = pd.read_csv(
        path3,
        parse_dates=["Transaction Date"],
    )

    df2["Record Timestamp"].max()

    end_mixer_time = df2["Record Timestamp"].max()
    start_mixer_time = df2["Record Timestamp"].min() - np.timedelta64(6, "h")

    raw_materials = df2["DESCRIPTION"].unique().tolist()

    df3 = df3[
        (
            (df3["Transaction Date"] >= start_mixer_time)
            & (df3["Transaction Date"] <= end_mixer_time)
            & (df3["Item Description"].isin(raw_materials))
        )
    ]

    st.dataframe(df3)

    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    csv = convert_df(df3)

    st.download_button(
        label="Download 'Hopper Transactions' as CSV",
        data=csv,
        file_name="Hopper Transactions.csv",
        mime="text/csv",
    )
