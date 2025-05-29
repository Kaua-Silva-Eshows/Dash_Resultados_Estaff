from data.dbconnect import get_dataframe_from_query
import streamlit as st

@st.cache_data
def companies(day,day2):
  return get_dataframe_from_query(f'''
    SELECT DISTINCT 
    E.ID as 'ID_Casa',
    E.NOME_FANTASIA as 'Casa'
    FROM T_DESPESA_RAPIDA DR 
    LEFT JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    WHERE E.FK_GRUPO_EMPRESA = 100
    AND STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') >= '{day}'
    AND STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') <= '{day2}'
    AND E.ID NOT IN (127,165,166,167,117,101,162,129,161,142,143,130,111,131)
    ORDER BY E.NOME_FANTASIA 
  ''', use_fabrica=True)

@st.cache_data
def inputs_expenses(day,day2):
  return get_dataframe_from_query(f'''
    SELECT 
    DRI.ID AS 'ID_Associac_Despesa_Item',
    E.ID AS 'ID_Casa',
    E.NOME_FANTASIA AS 'Casa',
    DR.ID AS 'ID_Despesa',
    F.ID AS 'ID_Fornecedor',
    LEFT(F.FANTASY_NAME, 23) AS 'Fornecedor',
    STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') AS 'Data_Competencia',
    I5.ID AS 'ID_Insumo',
    I5.DESCRICAO AS 'Insumo',
    I4.ID AS 'ID_Nivel_4',
    I4.DESCRICAO AS 'Nivel_4',
    I3.ID AS 'ID_Nivel_3',
    I3.DESCRICAO AS 'Nivel_3',
    I2.ID AS 'ID_Nivel_2',
    I2.DESCRICAO AS 'Nivel_2',
    I1.ID AS 'ID_Nivel_1',
    I1.DESCRICAO AS 'Nivel_1',
    ROUND(CAST(DRI.QUANTIDADE AS FLOAT), 3) AS 'Quantidade_Insumo',
    tudm.UNIDADE_MEDIDA_NAME AS 'Unidade_Medida',
    ROUND(CAST(DRI.VALOR AS FLOAT), 2) AS 'Valor_Insumo'
    FROM T_DESPESA_RAPIDA_ITEM DRI 
    INNER JOIN T_INSUMOS_NIVEL_5 I5 ON (DRI.FK_INSUMO = I5.ID)
    INNER JOIN T_INSUMOS_NIVEL_4 I4 ON (I5.FK_INSUMOS_NIVEL_4 = I4.ID)
    INNER JOIN T_INSUMOS_NIVEL_3 I3 ON (I4.FK_INSUMOS_NIVEL_3 = I3.ID)
    INNER JOIN T_INSUMOS_NIVEL_2 I2 ON (I3.FK_INSUMOS_NIVEL_2 = I2.ID)
    INNER JOIN T_INSUMOS_NIVEL_1 I1 ON (I2.FK_INSUMOS_NIVEL_1 = I1.ID)
    INNER JOIN ADMIN_USERS au ON (DRI.LAST_USER = au.ID)
    INNER JOIN T_DESPESA_RAPIDA DR ON (DRI.FK_DESPESA_RAPIDA = DR.ID)
    INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    INNER JOIN T_FORNECEDOR F ON (DR.FK_FORNECEDOR = F.ID)
    LEFT JOIN T_UNIDADES_DE_MEDIDAS tudm ON (I5.FK_UNIDADE_MEDIDA = tudm.ID)
    WHERE STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') >= '{day}'
    AND STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') <= '{day2}'
    AND I1.ID IN (100,101)
    AND E.FK_GRUPO_EMPRESA = 100
    ORDER BY DR.ID
  ''', use_fabrica=True)


@st.cache_data
def purchases_without_orders(day,day2):
  return get_dataframe_from_query(f'''
   WITH Ultimo_Status AS (
    SELECT
        FK_DESPESA_RAPIDA,
        MAX(ID) AS Ultimo_Status_ID
    FROM T_DESPESA_STATUS
    GROUP BY FK_DESPESA_RAPIDA
)
    SELECT
    DISTINCT DR.ID AS 'tdr_ID',
    E.NOME_FANTASIA AS 'Casa',
    LEFT(F.FANTASY_NAME, 23) AS 'Fornecedor',
    DR.NF AS 'Doc_Serie',
    STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') AS 'Data_Competencia',
    STR_TO_DATE(DR.VENCIMENTO, '%Y-%m-%d') AS 'Data_Vencimento',
    CCG1.DESCRICAO AS 'Class_Cont_Grupo_1',
    CCG2.DESCRICAO AS 'Class_Cont_Grupo_2',
    DR.OBSERVACAO AS 'Observacao',
    DR.VALOR_PAGAMENTO AS 'Valor_Original',
    DR.VALOR_LIQUIDO AS 'Valor_Liquido',
    CASE
	WHEN SP2.DESCRICAO = 'Provisionado' THEN 'Provisionado'
	     ELSE 'Real'
    END AS Status_Provisao_Real,
    SP.DESCRICAO AS 'Status_Pagamento',
    DATE_FORMAT(STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d'), '%m/%Y') AS Mes_Texto
    FROM T_DESPESA_RAPIDA DR
    INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    LEFT JOIN T_FORNECEDOR F ON (DR.FK_FORNECEDOR = F.ID)
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 CCG1 ON (DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = CCG1.ID)
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 CCG2 ON (DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = CCG2.ID)
    LEFT JOIN T_STATUS_PAGAMENTO SP ON (DR.FK_STATUS_PGTO = SP.ID)
    LEFT JOIN T_DESPESA_RAPIDA_ITEM tdri ON (DR.ID = tdri.FK_DESPESA_RAPIDA)
    LEFT JOIN Ultimo_Status US ON (DR.ID = US.FK_DESPESA_RAPIDA)
    LEFT JOIN T_DESPESA_STATUS DS ON (DR.ID = DS.FK_DESPESA_RAPIDA AND DS.ID = US.Ultimo_Status_ID)
    LEFT JOIN T_STATUS S ON (DS.FK_STATUS_NAME = S.ID)
    LEFT JOIN T_STATUS_PAGAMENTO SP2 ON (S.FK_STATUS_PAGAMENTO = SP2.ID)
    WHERE tdri.ID IS NULL
    AND DATE(DR.COMPETENCIA) >= '{day}'
    AND DATE(DR.COMPETENCIA) <= '{day2}'
    AND DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = 236
    AND E.FK_GRUPO_EMPRESA = 100
    ORDER BY DR.ID ASC
  ''', use_fabrica=True)  


@st.cache_data
def blueme_with_order(day,day2):
  return get_dataframe_from_query(f'''
    SELECT
        BP.tdr_ID AS ID_Despesa,
        BP.ID_Loja AS ID_Casa,
        BP.Loja AS Casa,
        BP.Fornecedor AS Fornecedor,
        BP.Doc_Serie AS Doc_Serie,
        STR_TO_DATE(BP.Data_Emissao, '%Y-%m-%d') AS Data_Competencia,
        STR_TO_DATE(BP.Data_Vencimento, '%Y-%m-%d') AS Data_Vencimento,
        BP.Valor_Original AS Valor_Original,
        BP.Valor_Liquido AS Valor_Liquido,
        BP.Valor_Insumos AS Valor_Cotacao,
        DATE_FORMAT(STR_TO_DATE(BP.Data_Emissao, '%Y-%m-%d'), '%m/%Y') AS Mes_Texto
      FROM View_BlueMe_Com_Pedido BP
      LEFT JOIN View_Insumos_Receb_Agrup_Por_Categ virapc ON BP.tdr_ID = virapc.tdr_ID
      WHERE DATE(BP.Data_Emissao) >= '{day}'
      AND DATE(BP.Data_Emissao) <= '{day2}'
  ''', use_fabrica=True)


@st.cache_data
def assoc_expense_items(day,day2):
  return get_dataframe_from_query(f'''
  SELECT 
  DRI.ID AS 'ID_Associac_Despesa_Item',
  E.ID AS 'ID_Casa',
  E.NOME_FANTASIA AS 'Casa',
  DR.ID AS 'ID_Despesa',
  STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') AS 'Data_Competencia',
  I5.ID AS 'ID_Insumo',
  I5.DESCRICAO AS 'Insumo',
  UM.UNIDADE_MEDIDA_NAME AS 'Unidade_Medida',                         
  CAST(REPLACE(DRI.QUANTIDADE, ',', '.') AS DECIMAL(10,2)) AS Quantidade_Insumo,
  DRI.VALOR / CAST(REPLACE(DRI.QUANTIDADE, ',', '.') AS DECIMAL(10,2)) AS Valor_Unitario,
  DRI.VALOR AS 'Valor_Total'
  FROM T_DESPESA_RAPIDA_ITEM DRI 
  INNER JOIN T_INSUMOS_NIVEL_5 I5 ON (DRI.FK_INSUMO = I5.ID)
  INNER JOIN T_INSUMOS_NIVEL_4 I4 ON (I5.FK_INSUMOS_NIVEL_4 = I4.ID)
  INNER JOIN T_INSUMOS_NIVEL_3 I3 ON (I4.FK_INSUMOS_NIVEL_3 = I3.ID)
  INNER JOIN T_INSUMOS_NIVEL_2 I2 ON (I3.FK_INSUMOS_NIVEL_2 = I2.ID)
  INNER JOIN T_INSUMOS_NIVEL_1 I1 ON (I2.FK_INSUMOS_NIVEL_1 = I1.ID)
  INNER JOIN ADMIN_USERS AU ON (DRI.LAST_USER = AU.ID)
  INNER JOIN T_DESPESA_RAPIDA DR ON (DRI.FK_DESPESA_RAPIDA = DR.ID)
  INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
  LEFT JOIN T_UNIDADES_DE_MEDIDAS UM ON (I5.FK_UNIDADE_MEDIDA = UM.ID)
  ''', use_fabrica=True)