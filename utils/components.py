import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid import GridUpdateMode
from st_aggrid import StAggridTheme 
from streamlit_echarts import st_echarts
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode


def component_hide_sidebar():
    st.markdown(""" 
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
                }
    </style>
    """, unsafe_allow_html=True)

def component_fix_tab_echarts():
    streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 450px; width: 750px;} 
   </style>
    """

    return st.markdown(streamlit_style, unsafe_allow_html=True)    

def component_effect_underline():
    st.markdown("""
    <style>
        .full-width-line-white {
            width: 100%;
            border-bottom: 1px solid #ffffff;
            margin-bottom: 0.5em;
        }
        .full-width-line-black {
            width: 100%;
            border-bottom: 1px solid #000000;
            margin-bottom: 0.5em;
        }
    </style>
    """, unsafe_allow_html=True)

def component_plotDataframe(df, name,height=400, num_columns=[], percent_columns=[]):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)

    # Palavras-chave para procurar colunas que contenham links
    keywords = ['VER DETALHES', 'VER CANDIDATOS', 'DISPARAR WPP', 'PERFIL ARTISTA']
    columns_with_link = [col_name for col_name in df.columns if any(keyword in col_name.upper() for keyword in keywords)]

     # Converter columns selecionadas para float com limpeza de texto
    for col in num_columns:
        if col in df.columns:
            df[f"{col}_NUM"] = (
                df[col]
                .astype(str)
                .str.upper()
                .str.replace(r'[A-Z$R\s]', '', regex=True)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
            )
            df[f"{col}_NUM"] = pd.to_numeric(df[f"{col}_NUM"], errors='coerce')

            # Agora formatar a coluna original como string BR
            df[col] = df[f"{col}_NUM"].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else ""
            )

    for col in percent_columns:
        if col in df.columns:
            df[f"{col}_NUM"] = (
                df[col]
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.replace('−', '-', regex=False)
                .str.replace('–', '-', regex=False)
                .str.replace(r'[^\d\.\-]', '', regex=True)
            )
            df[f"{col}_NUM"] = pd.to_numeric(df[f"{col}_NUM"], errors='coerce')

            # Agora formatar a coluna original como string percentual
            df[col] = df[f"{col}_NUM"].apply(
                lambda x: f"{x:.2f}%".replace('.', ',') if pd.notnull(x) else ""
            )

    # Configurar as opções do grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True)  # Habilitar filtro para todas as colunas
    
    cellstyle_code = JsCode("""
function(params) {
    const value = params.data[params.colDef.field + '_NUM'];
    if (value === null || value === undefined || isNaN(value)) {
        return {};
    }
    if (value < 0) {
        return {
            color: '#ff7b7b',
            fontWeight: 'bold'
        };
    }
    if (value > 0) {
        return {
            color: '#90ee90',
            fontWeight: 'bold'
        };
    }
    return {};
}
""")

    # Aplicar estilo nas colunas numéricas (valor ou porcentagem)
    for col in num_columns + percent_columns:
        if col in df.columns and f"{col}_NUM" in df.columns:
            gb.configure_column(col, cellStyle=cellstyle_code)
            gb.configure_column(f"{col}_NUM", hide=True, type=["numericColumn"])

    # Configurar a seleção de linhas (opcional)
    gb.configure_selection(
        selection_mode='multiple',  # 'single' ou 'multiple'
        use_checkbox=False,          # Habilitar caixas de seleção
        pre_selected_rows=[],
        suppressRowClickSelection=False  # Permite selecionar ao clicar em qualquer célula
    )

    # Construir opções do grid
    grid_options = gb.build()

    # Adicionar configurações adicionais para seleção de células
    grid_options.update({
        "enableRangeSelection": True,
        "suppressRowClickSelection": True,
        "cellSelection": True,
        "rowHeight": 40,  # Define a altura padrão das linhas
        "defaultColDef": {
            "flex": 1,
            "minWidth": 100,
            "autoHeight": False,  # Desativar auto-ajuste de altura para manter o espaçamento fixo
            "filter": True,  # Habilitar filtro para cada coluna
        }
    })

    custom_theme = (StAggridTheme(base="balham").withParams().withParts('colorSchemeDark'))

    # Exibir o DataFrame usando AgGrid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,  # Ajusta as colunas automaticamente ao carregar
        allow_unsafe_jscode=True,
        key=f"aggrid_{name}",
        theme=custom_theme,
        height=height
    )

    # Recupera o DataFrame filtrado
    
    filtered_df = grid_response['data']
    filtered_df = filtered_df.drop(columns=[col for col in filtered_df.columns if col.endswith('_NUM')], errors='ignore')
    return filtered_df, len(filtered_df)

def component_plotPizzaChart(labels, sizes, name, max_columns=8):
    chart_key = f"{labels}_{sizes}_{name}_"
    if name:
        st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    
    # Organize os dados para mostrar apenas um número limitado de categorias
    if len(labels) > max_columns:
        # Ordenar os dados e pegar os "max_columns" maiores
        sorted_data = sorted(zip(sizes, labels), reverse=True)[:max_columns]
        
        # Dados dos "Outros"
        others_value = sum(size for size, label in zip(sizes, labels) if (size, label) not in sorted_data)
        sorted_data.append((others_value, "Outros"))
        
        # Desempacotar os dados para labels e sizes
        sizes, labels = zip(*sorted_data)
    else:
        # Caso contrário, use todos os dados
        sizes, labels = sizes, labels

    # Preparar os dados para o gráfico
    data = [{"value": size, "name": label} for size, label in zip(sizes, labels)]
    
    options = {
    "tooltip": {
        "trigger": "item",
        "formatter": "{b}: {c} ({d}%)"
    },
    "legend": {
        "orient": "vertical",
        "left": "left",
        "top": "top",
        "textStyle": {
        "fontWeight": "bold",
        "color": "#FF6347",
        "overflow": "truncate",  # Isso vai cortar o texto se for muito grande
        "width": 100  # Define um limite de largura para o texto
    }
},
    "grid": {  
        "left": "50%", 
        "right": "50%", 
        "containLabel": True
    },
    "color": [
        "#D84C4C", "#FF6666", "#FF7878", "#FF8A8A",  
        "#FF9C9C", "#FFAEAE", "#FFC0C0", "#FFD2D2", "#FFE4E4"
    ],
    "series": [
        {
            "name": "Quantidade",
            "type": "pie",
            "radius": ["40%", "75%"],  
            "center": ["45%", "40%"],  
            "data": data,
            "label": {
                "show": False  # Garante que os rótulos não apareçam nas fatias
            },
            "labelLine": {
                "show": False  # Remove as linhas que puxam os rótulos
            },
            "minAngle": 5,  
            "itemStyle": {
                "borderRadius": 8,
                "borderColor": "#fff",
                "borderWidth": 2  
            },
            "selectedMode": "single",
            "selectedOffset": 8,  
            "emphasis": {
                "label": {
                    "show": False  # Impede que o rótulo apareça ao passar o mouse
                },
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }
    ]
}

    
    st_echarts(options=options, height="450px", key=chart_key)