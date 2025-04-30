import pandas as pd
import streamlit.components.v1 as components
import streamlit as st


def function_copy_dataframe_as_tsv(df):
    # Converte o DataFrame para uma string TSV
    df_tsv = df.to_csv(index=False, sep='\t')
    
    # Gera código HTML e JavaScript para copiar o conteúdo para a área de transferência
    components.html(
        f"""
        <style>
            .custom-button {{
                background-color: #1e1e1e; /* Cor de fundo escura */
                color: #ffffff; /* Cor do texto claro */
                border: 1px solid #333333; /* Cor da borda escura */
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                display: inline-block;
                text-align: center;
                text-decoration: none;
                transition: background-color 0.3s ease, color 0.3s ease;
            }}
            .custom-button:hover {{
                background-color: #333333; /* Cor de fundo escura ao passar o mouse */
                color: #e0e0e0; /* Cor do texto ao passar o mouse */
            }}
        </style>
        <textarea id="clipboard-textarea" style="position: absolute; left: -10000px;">{df_tsv}</textarea>
        <button class="custom-button" onclick="document.getElementById('clipboard-textarea').select(); document.execCommand('copy'); alert('DataFrame copiado para a área de transferência como TSV!');">Copiar DataFrame</button>
        """,
        height=100
    )

def function_merged_and_add_df(df1, df2, column):
    merged_df = pd.merge(df1, df2, on=f'{column}', how='outer', suffixes=('_df1', '_df2'))
    columns_to_sum = [col.split('_')[0] for col in merged_df.columns if '_df1' in col]
    for col in columns_to_sum:
        merged_df[f'{col}_total'] = merged_df[f'{col}_df1'].fillna(0) + merged_df[f'{col}_df2'].fillna(0)
    merged_df = merged_df.drop(columns=[col for col in merged_df.columns if '_df1' in col or '_df2' in col])
    merged_df = merged_df.rename(columns={col: col.replace('_total', '') for col in merged_df.columns if '_total' in col})

    merged_df[f'{column}'] = pd.to_datetime(merged_df[f'{column}'])
    merged_df = merged_df.sort_values(by=f'{column}')
    merged_df[f'{column}'] = pd.to_datetime(merged_df[f'{column}'], format="%m/%Y").dt.strftime("%m/%Y")

    return merged_df

def function_grand_total_line(df):
    row = pd.Series()
    row['Mês/Ano'] = '💰 Total Geral'
    row['Faturamento Total'] = df['Faturamento Total'].sum()
    row['C1 Impostos'] = df['C1 Impostos'].sum()
    row['C2 Custos de Ocupação'] = df['C2 Custos de Ocupação'].sum()
    row['C3 Despesas com Pessoal Interno'] = df['C3 Despesas com Pessoal Interno'].sum()
    row['C4 Despesas com Pessoal Terceirizado'] = df['C4 Despesas com Pessoal Terceirizado'].sum()
    row['C5 Despesas Operacionais com Freelas'] = df['C5 Despesas Operacionais com Freelas'].sum()
    row['C6 Despesas com Clientes'] = df['C6 Despesas com Clientes'].sum()
    row['C7 Despesas com Softwares e Licenças'] = df['C7 Despesas com Softwares e Licenças'].sum()
    row['C8 Despesas com Marketing'] = df['C8 Despesas com Marketing'].sum()
    row['C9 Despesas Financeiras'] = df['C9 Despesas Financeiras'].sum()
    row['Custos Totais'] = df['Custos Totais'].sum()
    df = pd.concat([df, row.to_frame().T], ignore_index=True)

    return df

def function_formated_cost(df, merged_df):
    for col in df.columns:
        if col not in ['Mês/Ano', 'Faturamento Total', 'Custos Totais']: 
            if (merged_df['Faturamento Total'].eq(0)).any():
                merged_df[f'{col[:2]}%'] = 0
            else:
                merged_df[f'{col[:2]}%'] = (merged_df[col] / merged_df['Faturamento Total']) * 100

    # Calcula o resultado total (faturamento - custo total)
    merged_df['Resultado Final'] = merged_df['Faturamento Total'] - merged_df['Custos Totais']

    # Adiciona a porcentagem de lucro
    merged_df['Res%'] = merged_df.apply(
        lambda row: (row['Resultado Final'] / row['Faturamento Total']) * 100 
        if row['Faturamento Total'] != 0 else 0, axis=1
    )

    for col in merged_df.columns:
        if col.endswith('%'):
            merged_df[col] = merged_df[col].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '0.00%')

    # Reorganiza as colunas
    cols_order = ['Mês/Ano', 'Faturamento Total','C1 Impostos', 'C1%', 'C2 Custos de Ocupação', 'C2%', 'C3 Despesas com Pessoal Interno', 'C3%', 
    'C4 Despesas com Pessoal Terceirizado', 'C4%', 'C5 Despesas Operacionais com Freelas', 'C5%', 'C6 Despesas com Clientes', 'C6%', 'C7 Despesas com Softwares e Licenças', 
    'C7%', 'C8 Despesas com Marketing', 'C8%', 'C9 Despesas Financeiras', 'C9%', 'Custos Totais', 'Resultado Final', 'Res%']
    merged_df = merged_df[cols_order]

    for col in merged_df.columns:
        if col in ['Faturamento Total','C1 Impostos','C2 Custos de Ocupação', 'C3 Despesas com Pessoal Interno', 
        'C4 Despesas com Pessoal Terceirizado', 'C5 Despesas Operacionais com Freelas', 'C6 Despesas com Clientes', 
        'C7 Despesas com Softwares e Licenças', 'C8 Despesas com Marketing', 'C9 Despesas Financeiras', 'Custos Totais', 'Resultado Final']:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
            merged_df[col] = merged_df[col].fillna(0)
            merged_df[col] = merged_df[col].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if isinstance(x, (int, float)) else x
            )
            

    return merged_df

def function_total_rows(df, category):
    row = pd.Series()
    cost_category = df[df['CATEGORIA DE CUSTO'] == f'{category}']
    for col in cost_category.columns:
        if col != 'CATEGORIA DE CUSTO' and col != 'CLASSIFICAÇÃO PRIMÁRIA':  # Exclui a coluna não numérica
            row[col] = cost_category[col].sum()
    row['CLASSIFICAÇÃO PRIMÁRIA'] = '📊 Total Categoria'
    last_position = df[df['CATEGORIA DE CUSTO'] == f'{category}'].index[-1]
    df = pd.concat([df.iloc[:last_position + 1], row.to_frame().T, df.iloc[last_position + 1:]]).reset_index(drop=True)

    return df

def function_format_numeric_columns(df, columns=[]):
    for column in columns:
        if column in df.columns:  
            try:
                df[column] = pd.to_numeric(df[column])  
                df[column] = df[column].apply(
                    lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                    if isinstance(x, (int, float)) else x
                )
            except Exception:
                continue 
    return df

def function_marged_pivot_costDetails(df1, df2):

    merged_df = pd.merge(
    df1,
    df2,
    on=["DATA", "CATEGORIA DE CUSTO", "CLASSIFICAÇÃO PRIMÁRIA"],  # Agora também estamos considerando a "CLASSIFICAÇÃO PRIMÁRIA"
    how="outer",  # Mantendo todos os dados de ambas as tabelas
    suffixes=('_costDetails', '_costsBluemeDetails')
)
    merged_df_grouped = merged_df.groupby(["DATA", "CATEGORIA DE CUSTO", "CLASSIFICAÇÃO PRIMÁRIA"]).agg({
        'VALOR_costDetails': 'sum',  
        'VALOR_costsBluemeDetails': 'sum' 
    }).reset_index()

    merged_df_grouped['VALOR_TOTAL'] = merged_df_grouped['VALOR_costDetails'].fillna(0) + merged_df_grouped['VALOR_costsBluemeDetails'].fillna(0)

    merged_df_grouped = merged_df_grouped.drop(columns=['VALOR_costDetails', 'VALOR_costsBluemeDetails'])
    merged_df_grouped = merged_df_grouped.rename(columns={'VALOR_TOTAL': 'VALOR'})

    pivot_df = merged_df_grouped.pivot_table(
    index=['CATEGORIA DE CUSTO', 'CLASSIFICAÇÃO PRIMÁRIA'], 
    columns='DATA', 
    values='VALOR', 
    aggfunc='sum',
    fill_value=0
    ).reset_index()
    
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c1_Impostos').any():
        pivot_df = function_total_rows(pivot_df, 'c1_Impostos')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c2_Custos_de_Ocupacao').any():
        pivot_df = function_total_rows(pivot_df, 'c2_Custos_de_Ocupacao')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c3_Despesas_com_Pessoal_Interno').any():
        pivot_df = function_total_rows(pivot_df, 'c3_Despesas_com_Pessoal_Interno')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c4_Despesas_com_Pessoal_Terceirizado').any():
        pivot_df = function_total_rows(pivot_df, 'c4_Despesas_com_Pessoal_Terceirizado')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c5_Despesas_Operacionais_com_Shows').any():
        pivot_df = function_total_rows(pivot_df, 'c5_Despesas_Operacionais_com_Shows')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c6_Despesas_com_Clientes').any():
        pivot_df = function_total_rows(pivot_df, 'c6_Despesas_com_Clientes')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c7_Despesas_com_Softwares_e_Licencas').any():
        pivot_df = function_total_rows(pivot_df, 'c7_Despesas_com_Softwares_e_Licencas')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c8_Despesas_com_Marketing').any():
        pivot_df = function_total_rows(pivot_df, 'c8_Despesas_com_Marketing')
    if (pivot_df['CATEGORIA DE CUSTO'] == 'c9_Despesas_Financeiras').any():
        pivot_df = function_total_rows(pivot_df, 'c9_Despesas_Financeiras')

    row = pd.Series()
    for col in pivot_df.columns:
        if col != 'CATEGORIA DE CUSTO' and col != 'CLASSIFICAÇÃO PRIMÁRIA':  
            row[col] = pivot_df.loc[~pivot_df['CLASSIFICAÇÃO PRIMÁRIA'].str.contains("📊 Total Categoria", na=False), col].sum()

    row['CATEGORIA DE CUSTO'] = '💰 Custo Geral'
    pivot_df = pd.concat([pivot_df, row.to_frame().T]).reset_index(drop=True)
    pivot_df['Total Do Periodo'] = pivot_df.drop(columns=['CATEGORIA DE CUSTO', 'CLASSIFICAÇÃO PRIMÁRIA']).sum(axis=1)
    pivot_df['CATEGORIA DE CUSTO'] = pivot_df['CATEGORIA DE CUSTO'].where(
    pivot_df['CATEGORIA DE CUSTO'].ne(pivot_df['CATEGORIA DE CUSTO'].shift())) 
    pivot_df = function_format_numeric_columns(pivot_df)

    return pivot_df

def function_total_line(df, column_value, column_total):
    
    df[column_value] = pd.to_numeric(df[column_value], errors='coerce')
    total_value = df[f'{column_value}'].sum()
    new_row = {
        f"{column_total}": "Total:", 
        f'{column_value}': total_value
    }

    for col in df.columns:
        if col not in [f"{column_total}", f'{column_value}']:
            new_row[col] = ""

    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    df = function_format_numeric_columns(df)


    return df

def funtion_calculate_percentage(new_value, old_value):
    percentage_difference = ((new_value - old_value) / old_value) * 100
    if percentage_difference < 0:
        percentage_color = 'red' 
        arrow = '▼'
    else:
        percentage_color = 'green'  
        arrow = '▲'
    return percentage_difference, percentage_color, arrow

def function_callsigns_structure(df, df2, colunm, tile, text, num=False, type=''):
    if type == 'sum':
        valuer1 = sum(df[f'{colunm}'])
        valuer2 = sum(df2[f'{colunm}'])
    elif type == 'average':
        valuer1 = df[f'{colunm}'].mean()
        valuer2 = df2[f'{colunm}'].mean()
    elif type == 'count':
        valuer1 = df[f'{colunm}'].count()
        valuer2 = df2[f'{colunm}'].count()

    percentage_difference, percentage_color, arrow = funtion_calculate_percentage(valuer1, valuer2)
    if num:
        valuer1_formatted = f"{valuer1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tile.write(f"<p style='text-align: center; font-size: 12px;'>{text}</br><span style='font-size: 17px;'>{valuer1_formatted}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)
    else:
        tile.write(f"<p style='text-align: center; font-size: 12px;'>{text}</br><span style='font-size: 17px;'>{valuer1}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)
