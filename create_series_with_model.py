import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def remove_online_courses(courses_df: pd.DataFrame) -> pd.DataFrame:
    df = courses_df.query("tp_modalidade_ensino != 2") # apenas cursos presenciais
    df = df.drop('tp_modalidade_ensino', axis = 1).reset_index(drop=True)
    return df

def remove_courses_in_more_than_one_region(courses_df: pd.DataFrame) -> pd.DataFrame:
    df = courses_df
    faculties_nunique_regions = df.groupby("co_ies")["no_regiao"].nunique()
    lista_cursos_apenas_uma_regiao = faculties_nunique_regions[faculties_nunique_regions == 1].index.to_list()
    df = df[df['co_ies'].isin(lista_cursos_apenas_uma_regiao)].reset_index(drop=True)
    return df

def get_cursos_df(parquet_path: str) -> pd.DataFrame:
    courses_df = pd.read_parquet(parquet_path)
    courses_df = remove_online_courses(courses_df)
    courses_df = remove_courses_in_more_than_one_region(courses_df)
    return courses_df

def sum_numeric_columns_by_co_ies_year(courses_df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = ['qt_vg_total', 'qt_ing', 'qt_conc', 'qt_mat', 'qt_inscrito_total']
    return courses_df.groupby(["co_ies", "nu_ano_censo"])[numeric_columns].sum().reset_index()

def create_last_year_metrics(time_series_df: pd.DataFrame) -> pd.DataFrame:
    df = time_series_df
    col_to_get_last_year = ['qt_conc', 'qt_mat', 'qt_inscrito_total']
    new_columns_names = ['qt_conc_ano_anterior', 'qt_mat_ano_anterior', 'qt_inscrito_ano_passado']
    df[new_columns_names] = df.groupby("co_ies")[col_to_get_last_year].shift(1)
    df = df.drop(col_to_get_last_year, axis = 1)
    df = df.dropna().reset_index(drop=True)
    return df

def map_column_values_by_institution(time_series_df, courses_df, col_name_to_map: str) -> pd.DataFrame:
    df = time_series_df
    column_mapper = courses_df.groupby("co_ies")[col_name_to_map].unique().to_dict()
    df[col_name_to_map] = df['co_ies'].map(column_mapper).apply(lambda x: x[0])
    return df

def make_boolean_columns(time_series_df: pd.DataFrame) -> pd.DataFrame:
    df = time_series_df
    df['sudeste'] = df.no_regiao == "Sudeste"
    tp_org_col_names = ['tp_org_acad_1','tp_org_acad_2', 'tp_org_acad_3','tp_org_acad_4','tp_org_acad_5']
    tp_cat_adm_col_names = ['tp_cat_adm_1','tp_cat_adm_2', 'tp_cat_adm_3','tp_cat_adm_4','tp_cat_adm_5', 'tp_cat_adm_7']
    df[tp_org_col_names] = pd.get_dummies(df.tp_organizacao_academica)
    df[tp_cat_adm_col_names] = pd.get_dummies(df.tp_categoria_administrativa)
    return df

def make_time_series(courses_df: pd.DataFrame, ies_df: pd.DataFrame) -> pd.DataFrame:
    time_series_df = sum_numeric_columns_by_co_ies_year(courses_df)
    time_series_df = create_last_year_metrics(time_series_df)
    time_series_df = map_column_values_by_institution(time_series_df, courses_df, 'no_regiao')
    time_series_df = map_column_values_by_institution(time_series_df, courses_df, 'no_uf')
    time_series_df = time_series_df.merge(ies_df, on=['co_ies', 'nu_ano_censo'])
    time_series_df = make_boolean_columns(time_series_df)    
    return time_series_df

print("Making time series dataframe...")
courses_df = get_cursos_df('cursos.parquet')
ies_df = pd.read_parquet('ies.parquet')
time_series_df = make_time_series(courses_df, ies_df)
print("Done.")

x_col = ['qt_vg_total', 
         'qt_conc_ano_anterior', 
         'qt_mat_ano_anterior',
         'qt_doc_total',
        'qt_tec_total',
        'tp_org_acad_1', 'tp_org_acad_4','tp_org_acad_5',
        'sudeste',
        'tp_cat_adm_1','tp_cat_adm_2', 'tp_cat_adm_3',
        'tp_cat_adm_4','tp_cat_adm_5', 'tp_cat_adm_7',
         ]

y_col = 'qt_ing'

print("Making model...")
rf_reg = RandomForestRegressor(random_state = 0, max_features="sqrt", n_estimators= 350)
rf_reg.fit(time_series_df[x_col], time_series_df[y_col])
print("Done.")

predictions = rf_reg.predict(time_series_df[x_col])
time_series_df['predictions'] = predictions
time_series_df['predictions'] = round(time_series_df['predictions'])

time_series_2022 = time_series_df.query("nu_ano_censo ==2022")

ies_name_mapper = time_series_2022.groupby("co_ies")["no_ies"].unique().to_dict()
time_series_df['no_ies_in_2022'] = time_series_df["co_ies"].map(ies_name_mapper)

time_series_df['nu_ano_censo'] = time_series_df['nu_ano_censo'].astype(int)
final_columns = ['co_ies', 'no_ies','no_uf', 'no_regiao', 'nu_ano_censo', 'qt_ing', 'predictions']
time_series_df[final_columns].to_parquet("time_series_predictions.parquet")