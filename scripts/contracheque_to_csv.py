import sys
from unidecode import unidecode
from pathlib import Path

import pandas as pd

from scripts.parsers import currency_to_float

"""
Os arquivos precisam ser salvos no formato `ano_mes_entidade.xls`.
Exemplo: `2020_04_prefeitura.xls`

O script funciona em arquivos `.xls` onde as duas primeiras linhas 
e as últimas 3 linhas são ignoradas.
No caso de erro 'Workbook corruption: seen[3] == 4' 
abra os arquivos xls dos contracheques, salvar como e tente novamente.
"""


def xls_from_folderpath(folder):
    folder = Path(folder)
    filepaths = folder.glob("*.xls")
    return filepaths


def get_filepath_atts(filepath):
    filename = filepath.split("/")[-1]
    name, _ = filename.split(".")
    year, month, area = name.split("_")
    return year, month, area


def concat_xls(filepaths):
    filepaths = list(filepaths)
    if not filepaths:
        print("Error: No xls files in the folder")
        sys.exit()

    df_list = []

    for path in filepaths:
        path = str(path)
        df = pd.read_excel(path, skiprows=(0, 1))
        df.drop(df.tail(3).index, inplace=True)
        year, month, area = get_filepath_atts(path)
        df["year"] = year
        df["month"] = month89
        df["area"] = area
        df_list.append(df)

    return pd.concat(df_list)


def transform_df(df):
    column_list = []

    for column in df.columns:
        column = column.lower()
        column = column.replace(" ", "_")
        column = unidecode(column)
        column_list.append(column)

    df.columns = column_list

    df["salario_base"] = df["salario_base"].apply(currency_to_float)
    df["salario_vantagens"] = df["salario_vantagens"].apply(currency_to_float)
    df["salario_gratificacao"] = df["salario_gratificacao"].apply(currency_to_float)

    return df


if len(sys.argv) < 2:
    print("Error: Missing folder name as parameter")
    print("eg: > python contracheque_to_csv.py /User/name/folder")
    sys.exit()

folder = sys.argv[1]

filepaths = xls_from_folderpath(folder)

df = concat_xls(filepaths)

df = transform_df(df)

csv_path = str(folder) + "/contracheques.csv"
df.to_csv(csv_path, index=False)
print(f"File saved in {csv_path}")
