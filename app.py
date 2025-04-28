import streamlit as st
from EchoFabric import get_call_insight
import pandas as pd
from pretty_html_table import build_table

audio_file = st.file_uploader("Upload an audio file (MP3 or WAV)", type=["mp3", "wav"])

if audio_file is not None:
    df=get_call_insight(audio_file)

    html_table_blue_light = build_table(df, 'green_light', font_family='verdana', escape=False, index=True)
    st.markdown(html_table_blue_light, unsafe_allow_html=True)
    # st.table(display_df)

    csv = df.to_csv(index=True).encode('utf-8-sig')
    st.download_button("Download csv", csv, "call_insight.csv", "text/csv", key='download-csv')