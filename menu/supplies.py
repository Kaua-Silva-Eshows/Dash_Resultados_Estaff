import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from data.querys_blueme import *
from menu.page import Page
from utils import *
from utils.components import *
from utils.functions import *


def BuildSupplies(companies_, inputsExpenses, purchasesWithoutOrders, bluemeWithOrder, assocExpenseItems):

    tabs = st.tabs(["Análises", "Processos"])

    with tabs[0]:

        row = st.columns(6)
        global day_analysis, day_analysis2
        #Filtro de data
        with row[2]:
            day_analysis = st.date_input('Data Inicio:', value=datetime.today().replace(day=1).date(), format='DD/MM/YYYY', key='day_analysis') 
        with row[3]:
            day_analysis2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_analysis2')
        #Precalção de erro
        if day_analysis > day_analysis2:
            st.warning('📅 Data Inicio deve ser menor que Data Final')
        
        else:
            inputsExpenses = inputs_expenses(day_analysis, day_analysis2)

            #Filtro de Casas
            row_companies = st.columns([1,1,1])
            with row_companies[1]:
                companies_filtered = st.multiselect('Selecione a(s) Casa(s):',options=sorted(inputsExpenses['Casa'].dropna().unique()), placeholder='Casas')
            #Caso nenhum esteja selecionado mostra todos
            if not companies_filtered:
                companies_filtered = inputsExpenses['Casa'].dropna().unique()

            inputsExpenses_filtered = inputsExpenses[inputsExpenses['Casa'].isin(companies_filtered)]
            #Agrupa por Casa e Categoria
            inputsExpenses_n2 = (inputsExpenses_filtered.groupby(['Casa', 'Nivel_2'])[['Valor_Insumo']].sum().reset_index().sort_values(by=['Casa', 'Valor_Insumo'], ascending=[True, False]))
            inputsExpenses_n2 = function_format_number_columns(inputsExpenses_n2, ['Valor_Insumo'])
            #Agrupa por Categoria
            categoryN2_grafic = (inputsExpenses_filtered.groupby('Nivel_2')[['Valor_Insumo']].sum().reset_index().sort_values(by='Valor_Insumo', ascending=False))
            categoryN2_grafic['Percentual'] = (categoryN2_grafic['Valor_Insumo'] / categoryN2_grafic['Valor_Insumo'].sum() * 100).round(1)
            categoryN2_grafic['Label'] = categoryN2_grafic.apply(lambda x: f"{x['Nivel_2']} ({x['Percentual']}%)", axis=1)

            col1, col2 = st.columns([1, 0.8])

            with col1:
                component_plotDataframe(inputsExpenses_n2, 'Insumos por Casa e Categoria')
                function_copy_dataframe_as_tsv(inputsExpenses_n2)
            
            with col2:
                component_plotPizzaChart(categoryN2_grafic['Label'], categoryN2_grafic['Valor_Insumo'], 'Gastos por Categoria', 19)

            st.markdown('---')

            row_categoryN2 = st.columns([1,1,1])
            with row_categoryN2[1]:
                categoryN2_selected = st.multiselect('Selecione a(s) Categoria(s) (Nivel 2):',options=sorted(inputsExpenses['Nivel_2'].dropna().unique()), placeholder='Categorias')

            if not categoryN2_selected:
                categoryN2_selected = inputsExpenses['Nivel_2'].dropna().unique()

            categoryN2 = inputsExpenses[inputsExpenses['Nivel_2'].isin(categoryN2_selected)]

            col3, col4 = st.columns([1, 1])

            with col3:
                categoryN2_supplier_companies = (categoryN2.groupby(['Casa', 'Fornecedor'])[['Valor_Insumo']].sum().reset_index().sort_values(by=['Casa', 'Valor_Insumo'], ascending=[True, False]))
                
                categoryN2_supplier_companies = function_format_number_columns(categoryN2_supplier_companies, ['Valor_Insumo'])
                
                component_plotDataframe(categoryN2_supplier_companies, 'Insumos por Casa e Fornecedor')
                function_copy_dataframe_as_tsv(categoryN2_supplier_companies)

            with col4:
                categoryN2_supplier = (categoryN2.groupby('Fornecedor')[['Valor_Insumo']].sum().reset_index().sort_values(by='Valor_Insumo', ascending=False))
                categoryN2_supplier['Percentual'] = (categoryN2_supplier['Valor_Insumo'] / categoryN2_supplier['Valor_Insumo'].sum() * 100).round(1)

                categoryN2_supplier = function_format_number_columns(categoryN2_supplier, ['Valor_Insumo'])
                categoryN2_supplier['Valor Gasto (R$)'] = categoryN2_supplier['Valor_Insumo']
                
                component_plotDataframe(categoryN2_supplier[['Fornecedor', 'Valor Gasto (R$)', 'Percentual']], 'Distribuição por Fornecedor', column_config= {"Percentual": st.column_config.ProgressColumn("Percentual",format="%.1f%%", min_value=0, max_value=100)})
            
            st.markdown('---')

            categoryN2_inputs = (categoryN2.groupby('Insumo')[['Valor_Insumo', 'Quantidade_Insumo']].sum().reset_index())
            categoryN2_inputs['Preco_Medio'] = categoryN2_inputs['Valor_Insumo'] / categoryN2_inputs['Quantidade_Insumo']
            categoryN2_inputs['Percentual_Repres'] = (categoryN2_inputs['Valor_Insumo'] / categoryN2_inputs['Valor_Insumo'].sum() * 100).round(1)
            categoryN2_inputs = categoryN2_inputs.sort_values(by='Valor_Insumo', ascending=False)

            #Pegando primeiro e ultimo dia do mês passado para calcular preço médio anterior
            last_day_last_month = datetime.today().replace(day=1) - pd.Timedelta(days=1)
            first_day_last_month = (datetime.today().replace(day=1) - pd.Timedelta(days=1)).replace(day=1)
            
            categoryN2_inputs_last_month = inputs_expenses(first_day_last_month.strftime('%Y-%m-%d'), last_day_last_month.strftime('%Y-%m-%d'))
            categoryN2_inputs_last_month = (categoryN2_inputs_last_month.groupby('Insumo')[['Valor_Insumo', 'Quantidade_Insumo']].sum().reset_index())
            categoryN2_inputs_last_month['Preco_Medio_Anterior'] = categoryN2_inputs_last_month['Valor_Insumo'] / categoryN2_inputs_last_month['Quantidade_Insumo']
            categoryN2_inputs_last_month = categoryN2_inputs_last_month[['Insumo', 'Preco_Medio_Anterior']]
            
            #Faz o merge e calcula a variação percentual
            categoryN2_inputs_merged = categoryN2_inputs.merge(categoryN2_inputs_last_month, on='Insumo', how='left')
            categoryN2_inputs_merged['Variacao_Percentual'] = ((categoryN2_inputs_merged['Preco_Medio'] - categoryN2_inputs_merged['Preco_Medio_Anterior']) / categoryN2_inputs_merged['Preco_Medio_Anterior'] * 100)

            #Formatação das colunas
            categoryN2_inputs_merged = function_format_number_columns(categoryN2_inputs_merged, ['Valor_Insumo', 'Quantidade_Insumo', 'Preco_Medio', 'Preco_Medio_Anterior'])
            categoryN2_inputs_merged['Percentual_Repres'] = categoryN2_inputs_merged['Percentual_Repres'].map(lambda x: f"{x:.1f}%")
            categoryN2_inputs_merged['Variacao_Percentual'] = categoryN2_inputs_merged['Variacao_Percentual'].map(lambda x: f"{x:+.1f}%" if pd.notnull(x) else '-')
            categoryN2_inputs_merged_style = categoryN2_inputs_merged.style.map(function_highlight_percentage, subset=['Variacao_Percentual'], invert_color=True)

            component_plotDataframe(categoryN2_inputs_merged_style, 'Detalhamento por Insumo')
            function_copy_dataframe_as_tsv(categoryN2_inputs_merged)

    with tabs[1]:

        row2 = st.columns(6)
        global day_process, day_process2
        #Filtro de data
        with row2[2]:
            day_process = st.date_input('Data Inicio:', value=datetime.today().replace(day=1).date(), format='DD/MM/YYYY', key='day_process') 
        with row2[3]:
            day_process2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_process2')
        #Precalção de erro
        if day_process > day_process2:
            st.warning('📅 Data Inicio deve ser menor que Data Final')
        
        else:
            #Puxando a base de empresas
            companies_ = companies(day_process, day_process2)
            #Filtro de Casas
            row_companies2 = st.columns([1,1,1])
            with row_companies2[1]:
                companies_selected = st.multiselect('Selecione a(s) Casa(s):',options=sorted(companies_['Casa'].dropna().unique()), placeholder='Casas')
            #Caso nenhum esteja selecionado mostra todos
            if not companies_selected:
                companies_selected = companies_['Casa'].dropna().unique()

            with st.expander('Compras Sem Pedido', expanded=True):
                st.warning('Não devem ocorrer')
                st.markdown('---')

                #Puxando a base de Compras Sem Pedido
                purchasesWithoutOrders = purchases_without_orders(day_process, day_process2)
                purchasesWithoutOrders = purchasesWithoutOrders[purchasesWithoutOrders['Casa'].isin(companies_selected)]

                #Agrupar e somar (antes de formatar!)
                purchasesWithoutOrders_grouped = (purchasesWithoutOrders.groupby('Casa').agg(Valor_Original=('Valor_Original', 'sum'), Valor_Liquido=('Valor_Liquido', 'sum'), Quantidade_Despesas=('Valor_Original', 'count')).reset_index())

                # Criar coluna de Percentual
                purchasesWithoutOrders_grouped['Percentual'] = (purchasesWithoutOrders_grouped['Valor_Original'] / purchasesWithoutOrders_grouped['Valor_Original'].sum() * 100).round(1)

                purchasesWithoutOrders_grouped = function_format_number_columns(purchasesWithoutOrders_grouped, ['Valor_Original', 'Valor_Liquido'])
                # Exibir com as colunas configuradas
                component_plotDataframe(purchasesWithoutOrders_grouped[['Casa', 'Quantidade_Despesas', 'Valor_Original', 'Valor_Liquido', 'Percentual']], 'Compras Sem Pedido', column_config={
                    "Quantidade_Despesas": st.column_config.TextColumn(
                        "Qtd. Despesas"
                    ),
                    "Valor_Original": st.column_config.TextColumn(
                        "Valor Original (R$)"
                    ),
                    "Valor_Liquido": st.column_config.TextColumn(
                        "Valor Líquido (R$)"
                    ),
                    "Percentual": st.column_config.ProgressColumn(
                        "Percentual do Total",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    )
                })

                purchasesWithoutOrders = purchasesWithoutOrders.sort_values(by=['Casa', 'Valor_Original'], ascending=[True, False])
                purchasesWithoutOrders = function_format_number_columns(purchasesWithoutOrders, ['Valor_Original', 'Valor_Liquido'])
                component_plotDataframe(purchasesWithoutOrders, 'Base Sem Pedido Completa')
                function_copy_dataframe_as_tsv(purchasesWithoutOrders)

            st.markdown('---')

            with st.expander('Distorções (Valor da Despesa - Valor dos Insumos)', expanded=True):

                st.markdown('---')
                
                # Puxando a base de insumos nas despesas
                bluemeWithOrder = blueme_with_order(day_process, day_process2)

                bluemeWithOrder = bluemeWithOrder[bluemeWithOrder['Casa'].isin(companies_selected)]

                # Calcular divergência
                bluemeWithOrder['Divergencia'] = bluemeWithOrder['Valor_Original'] - bluemeWithOrder['Valor_Cotacao']
                bluemeWithOrder = bluemeWithOrder[bluemeWithOrder['Divergencia'] != 0]
                
                #Ordenar por Casa (ascendente) e Divergência (decrescente)
                bluemeWithOrder = bluemeWithOrder.sort_values(by=['Casa', 'Divergencia'], ascending=[True, False])                   

                # Ajustando formato BR
                #bluemeWithOrder = function_format_number_columns(bluemeWithOrder, ['Valor_Original', 'Valor_Liquido', 'Valor_Cotacao'])  

                if bluemeWithOrder.empty:
                    st.warning("Nenhum dado com distorção encontrado.")
                else:
                    col1, col2 = st.columns([2, 1]) 
                    with col1:
                        assocExpenseItems = assoc_expense_items(day_process, day_process2)
                        bluemeWithOrder['Data_Competencia'] = bluemeWithOrder['Data_Competencia'].astype(str)
                        bluemeWithOrder['Data_Vencimento'] = bluemeWithOrder['Data_Vencimento'].astype(str)
                        bluemeWithOrder_copy = bluemeWithOrder.copy()
                        assocExpenseItems['Data_Competencia'] = assocExpenseItems['Data_Competencia'].astype(str)
                        bluemeWithOrder = function_format_number_columns(bluemeWithOrder, ['Divergencia', 'Valor_Original', 'Valor_Liquido', 'Valor_Cotacao'])
                        assocExpenseItems = function_format_number_columns(assocExpenseItems, ['Quantidade_Insumo', 'Valor_Unitario', 'Valor_Total'])
                        component_plotDataframe_aggrid(bluemeWithOrder, 'Detalhamento das Distorções', num_columns=['Divergencia'], df_details=assocExpenseItems, coluns_merge_details='ID_Despesa', coluns_name_details='Casa' ,key="grid_distorcoes")
                    
                    with col2:
                        # Agrupar por casa e calcular quantidade e valor total da divergência
                        bluemeWithOrder_divergence = (bluemeWithOrder_copy.groupby('Casa').agg(Quantidade=('Divergencia', 'count'),Valor_Total_Distorcido=('Divergencia', 'sum')).reset_index().sort_values(by='Valor_Total_Distorcido', ascending=False))
                        # Ordenar do maior para o menor valor total distorcido
                        bluemeWithOrder_divergence = bluemeWithOrder_divergence.sort_values(by='Valor_Total_Distorcido', ascending=False)
                        bluemeWithOrder_divergence = function_format_number_columns(bluemeWithOrder_divergence, ['Valor_Total_Distorcido'])

                        bluemeWithOrder_style = bluemeWithOrder_divergence.style.map(function_highlight_value, ['Valor_Total_Distorcido'])
                        component_plotDataframe(bluemeWithOrder_style, 'Resumo por Casa')
                
                # Puxando a base de insumos nas despesas

                # Ajustando formato BR
                assocExpenseItems = function_format_number_columns(assocExpenseItems, ['Quantidade_Insumo', 'Valor_Unitario', 'Valor_Total'])  

                # Exibir os insumos da despesa selecionada
                # if selected_rows is not None and len(selected_rows) > 0:
                #     input_id = selected_rows.iloc[0]['ID_Despesa']
                #     assocExpenseItems_filtered = assocExpenseItems[assocExpenseItems['ID_Despesa'] == input_id]

                #     component_plotDataframe(assocExpenseItems_filtered, f'Despesa ID:{input_id}')
                #     function_copy_dataframe_as_tsv(assocExpenseItems_filtered)
                # else:
                #     st.info("Selecione uma despesa com distorção para visualizar os itens.")

class Supplies(Page):
    def render(self):
        self.data = {}
        day_analysis = datetime.today().replace(day=1).date()
        day_analysis2 = datetime.today().date()
        day_process = datetime.today().replace(day=1).date()
        day_process2 = datetime.today().date()
        self.data['companies_'] = companies(day_process, day_process2)
        self.data['inputsExpenses'] = inputs_expenses(day_analysis, day_analysis2)
        self.data['purchasesWithoutOrders'] = purchases_without_orders(day_process, day_process2)
        self.data['bluemeWithOrder'] = blueme_with_order(day_process, day_process2)
        self.data['assocExpenseItems'] = assoc_expense_items(day_process, day_process2)

        BuildSupplies(self.data['companies_'],
                      self.data['inputsExpenses'],
                      self.data['purchasesWithoutOrders'],
                      self.data['bluemeWithOrder'],
                      self.data['assocExpenseItems'])