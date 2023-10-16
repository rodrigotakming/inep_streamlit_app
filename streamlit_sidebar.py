import pandas as pd
import streamlit as st

def create_ies_multiselect(data_frame):
    return st.sidebar.multiselect('Selecione a IES:',
                                  data_frame['no_ies'].sort_values().unique())

def create_region_multiselect(data_frame):
    return st.sidebar.multiselect('Selecione a Região:',
                                  data_frame['no_regiao'].sort_values().unique())

def create_state_multiselect(data_frame):
    return st.sidebar.multiselect('Selecione o Estado:',
                                  data_frame['no_uf'].sort_values().unique())

def create_start_date_input():
    return st.sidebar.selectbox(
        "Selecione Ano Início:",
        [*range(2009, 2022)])

def create_end_date_input():
    return st.sidebar.selectbox(
        "Selecione Ano Fim:",
        [*range(2010, 2023)],
        12)

def filter_data_frame_if_selected(data_frame: pd.DataFrame, selection: list[str], column: str) -> pd.DataFrame:
    df = data_frame.copy()
    if selection:
        df = df[df[column].isin(selection)]
    return df


def streamlit_sidebar(data_frame: pd.DataFrame):
    region_selection = create_region_multiselect(data_frame)

    filtering_df = data_frame.copy()

    filtering_df = filter_data_frame_if_selected(filtering_df, region_selection, "no_regiao")

    state_selection = create_state_multiselect(filtering_df)

    filtering_df = filter_data_frame_if_selected(filtering_df, state_selection, "no_uf")

    ies_selection = create_ies_multiselect(filtering_df)

    filter_year_start = create_start_date_input()

    filter_year_end = create_end_date_input()
    
    return region_selection, state_selection, ies_selection, filter_year_start, filter_year_end