import pandas as pd
import streamlit as st
from streamlit_sidebar import streamlit_sidebar, filter_data_frame_if_selected
import plotly.express as px

def render_dash():

    time_series_df = pd.read_parquet("parquet_files/time_series_predictions.parquet")

    region_selection, state_selection, ies_selection, filter_year_start, filter_year_end \
          = streamlit_sidebar(time_series_df)
    
    time_series_df = time_series_df.query("nu_ano_censo >= @filter_year_start and nu_ano_censo <= @filter_year_end").reset_index(drop=True)

    st.header('Modelo Previsão de ingresso de alunos.')

    time_series_df = filter_data_frame_if_selected(time_series_df, region_selection, "no_regiao")
    time_series_df = filter_data_frame_if_selected(time_series_df, state_selection, "no_uf")
    time_series_df = filter_data_frame_if_selected(time_series_df, ies_selection, "no_ies")

    time_series_to_plot = time_series_df.groupby("nu_ano_censo")[["qt_ing", "predictions"]].sum()

    rename_col = {
        'qt_ing': 'Valor Real',           
        'predictions': 'Predição do Modelo'
        }

    time_series_to_plot = time_series_to_plot.rename(columns=rename_col)

    px_line = px.line(time_series_to_plot, 
                      x = [str(year) for year in time_series_to_plot.index], 
                      y = time_series_to_plot.columns.to_list(),
                      title = "Previsão das seleções",
                      markers=True)
    
    px_line.update_layout(
                        xaxis_title="Ano",
                        xaxis_title_font=dict(size=20),
                        yaxis_title="Total de Alunos",
                        yaxis_title_font=dict(size=20),
                        legend_title_text='Legenda:',
                    )
    
    
    px_line.update_traces(line=dict(color='#748cab'), selector=dict(name='Valor Real'))
    px_line.update_traces(line=dict(color='red', dash='dash', width=3), selector=dict(name='Predição do Modelo'))

    
    st.plotly_chart(px_line, use_container_width = True, use_container_height = True)
    st.divider()
    st.caption('Fonte: INEP (2022) - Censo 2010 até 2022 de cursos presenciais')
    

    
render_dash()