from matplotlib.dates import relativedelta
import pandas as pd
import streamlit as st
from data.querys_blueme import *
from data.querys_estaff import *
from data.querys_grupoe import *
from menu.page import Page
from utils.components import *
from utils.functions import *
from datetime import date, datetime

def BuildGeneralResults(billingCompanies, worksByFunctions, generalRevenueEvents, generalRevenueBrigada):

    row1 = st.columns(6)
    global day_GeneralResults1, day_GeneralResults2

    with row1[2]:
        day_GeneralResults1 = st.date_input('Data Inicio:', value=date(datetime.today().year, datetime.today().month, 1) - relativedelta(months=1), format='DD/MM/YYYY', key='day_GeneralResults1') 
    with row1[3]:
        day_GeneralResults2 = st.date_input('Data Final:', value=date(datetime.today().year, datetime.today().month, 1) - relativedelta(days=1), format='DD/MM/YYYY', key='day_GeneralResults2')

    day_GeneralResults3 = day_GeneralResults1 - relativedelta(months=1)
    day_GeneralResults4 = day_GeneralResults2 - relativedelta(months=1)


    row2 = st.columns([2,1.5])
    billingCompanies = billing_companies(day_GeneralResults1, day_GeneralResults2)
    worksByFunctions = works_by_functions(day_GeneralResults1, day_GeneralResults2)
    
    billingCompanies2 = billing_companies(day_GeneralResults3, day_GeneralResults4)
    worksByFunctions2 = works_by_functions(day_GeneralResults3, day_GeneralResults4)

    with row2[0]:
            
        row2_1 = st.columns(5)
        tile = row2_1[0].container(border=True)

        sum_total_works = sum(billingCompanies['NÚM. DE TRABALHOS'])
        sum_total_works2 = sum(billingCompanies2['NÚM. DE TRABALHOS'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_total_works, sum_total_works2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Núm. Jobs</br><span style='font-size: 18px;'>{sum_total_works}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_1[1].container(border=True)
        sum_total_freelas = sum(billingCompanies['FREELAS DISTINTOS'])
        sum_total_freelas2 = sum(billingCompanies2['FREELAS DISTINTOS'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_total_freelas, sum_total_freelas2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Freelas Dist.</br><span style='font-size: 18px;'>{sum_total_freelas}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_1[2].container(border=True)
        sum_total_functions = sum(billingCompanies['FUNÇÕES DISTINTAS'])
        sum_total_functions2 = sum(billingCompanies2['FUNÇÕES DISTINTAS'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_total_functions, sum_total_functions2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Funções Dist.</br><span style='font-size: 18px;'>{sum_total_functions}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_1[3].container(border=True)
        mean_value_for_hour = billingCompanies['VALOR LIQUIDO'].mean()
        mean_value_for_hour2 = billingCompanies2['VALOR LIQUIDO'].mean()
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(mean_value_for_hour, mean_value_for_hour2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Valor Med./Jobs</br><span style='font-size: 18px;'>{mean_value_for_hour:.2f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_1[4].container(border=True)
        mean_value_for_hour = worksByFunctions['VALOR MÉDIO POR HORA'].mean()
        mean_value_for_hour2 = worksByFunctions2['VALOR MÉDIO POR HORA'].mean()
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(mean_value_for_hour, mean_value_for_hour2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Valor Med./Hora</br><span style='font-size: 18px;'>{mean_value_for_hour:.2f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        row2_2 = st.columns(5)

        tile = row2_2[0].container(border=True)
        sum_value_proposal = sum(billingCompanies['VALOR LIQUIDO'])
        sum_value_proposal2 = sum(billingCompanies2['VALOR LIQUIDO'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_value_proposal, sum_value_proposal2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Valor Propostas</br><span style='font-size: 18px;'>{sum_value_proposal:,.1f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_2[1].container(border=True)
        sum_value_extra = sum(billingCompanies['VALOR EXTRA'])
        sum_value_extra2 = sum(billingCompanies2['VALOR EXTRA'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_value_extra, sum_value_extra2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Valor Extra</br><span style='font-size: 18px;'>{sum_value_extra:,.1f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_2[2].container(border=True)
        sum_value_freelas = sum(billingCompanies['VALOR FREELA'])
        sum_value_freelas2 = sum(billingCompanies2['VALOR FREELA'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_value_freelas, sum_value_freelas2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Valor Freelas</br><span style='font-size: 18px;'>{sum_value_freelas:,.1f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_2[3].container(border=True)
        sum_value_gross = sum(billingCompanies['VALOR BRUTO'])
        sum_value_gross2 = sum(billingCompanies2['VALOR BRUTO'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_value_gross, sum_value_gross2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Valor Bruto</br><span style='font-size: 18px;'>{sum_value_gross:,.1f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        tile = row2_2[4].container(border=True)
        sum_estaff_value = sum(billingCompanies['TAXA ESTAFF'])
        sum_estaff_value2 = sum(billingCompanies2['TAXA ESTAFF'])
        percentage_difference, percentage_color, arrow = funtion_calculate_percentage(sum_estaff_value, sum_estaff_value2)
        tile.write(f"<p style='text-align: center; font-size: 12px;'>Fat. Estaff</br><span style='font-size: 18px;'>{sum_estaff_value:,.2f}</span></br><span style='font-size: 10px; color: {percentage_color};'>{percentage_difference:.2f}% {arrow}</span></p>", unsafe_allow_html=True)

        billingCompanies = billingCompanies.drop(columns=['VALOR LIQUIDO', 'VALOR EXTRA', 'VALOR FREELA', 'VALOR BRUTO'])
        billingCompanies = function_format_numeric_columns(billingCompanies, ['VALOR TRANSACIONADO', 'TAXA ESTAFF'])
        filtered_copy, count = component_plotDataframe(billingCompanies, "Faturamento Por Estabelecimento")
        function_copy_dataframe_as_tsv(filtered_copy)

    with row2[1]:
        worksByFunctions = function_format_numeric_columns(worksByFunctions, ['VALOR MÉDIO POR HORA'])
        filtered_copy, count = component_plotDataframe(worksByFunctions, "Trabalhos Por Funções",height=631)
        function_copy_dataframe_as_tsv(filtered_copy)
    
    with st.expander("📊 Abertura por Evento Geral", expanded=False):
        generalRevenueEvents = general_revenue_events(day_GeneralResults1, day_GeneralResults2, filters='')
        generalRevenueEvents = function_format_numeric_columns(generalRevenueEvents, ['VALOR BRUTO', 'VALOR LIQUIDO', 'CUSTO EXTRA', 'TAXA EVENTO'])
        filtered_copy, count = component_plotDataframe(generalRevenueEvents, "Abertura Geral por Evento")
        function_copy_dataframe_as_tsv(filtered_copy)
        #function_box_lenDf(len_df=count, df=filtered_copy, y='-100', x='500', box_id='box1', item='Propostas')

    with st.expander("📊 Abertura por Brigada Geral", expanded=False):
        generalRevenueBrigada = general_revenue_brigada(day_GeneralResults1, day_GeneralResults2, filters='')
        generalRevenueBrigada = function_format_numeric_columns(generalRevenueBrigada, ['VALOR CONTRATO', 'PARCELA 1', 'PARCELA 2', 'PARCELA 3', 'PARCELA 4', 'PARCELA 5'])
    
        filtered_copy, count = component_plotDataframe(generalRevenueBrigada, "Abertura Geral por Brigada")
        function_copy_dataframe_as_tsv(filtered_copy)
        #function_box_lenDf(len_df=count, df=filtered_copy, y='-100', x='500', box_id='box1', item='Propostas')


class GeneralResults():
    def render(self):
        self.data = {}
        day_GeneralResults1 = date(datetime.today().year, datetime.today().month, 1) - relativedelta(months=1)
        day_GeneralResults2 = date(datetime.today().year, datetime.today().month, 1) - relativedelta(days=1)
        self.data['billingCompanies'] = billing_companies(day_GeneralResults1, day_GeneralResults2)
        self.data['worksByFunctions'] = works_by_functions(day_GeneralResults1, day_GeneralResults2) 
        self.data['generalRevenueEvents'] = general_revenue_events(day_GeneralResults1, day_GeneralResults2, filters='')
        self.data['generalRevenueBrigada'] = general_revenue_brigada(day_GeneralResults1, day_GeneralResults2, filters='')
        
        BuildGeneralResults(self.data['billingCompanies'], 
                            self.data['worksByFunctions'],
                            self.data['generalRevenueEvents'],
                            self.data['generalRevenueBrigada'])
