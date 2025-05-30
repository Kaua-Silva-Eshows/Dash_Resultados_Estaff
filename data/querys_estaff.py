from data.dbconnect import get_dataframe_from_query
import streamlit as st

@st.cache_data
def general_revenue(day1, day2, filters):
    return get_dataframe_from_query(f"""
WITH PROPOLS AS (
    SELECT
        DATE_FORMAT(TO2.START_AT, '%m/%Y') AS DATA,
        COUNT(TP.ID) AS NUM_JOBS_B2B,
        SUM(TO2.VALUE) AS VALOR_OPORTUNIDADE,
        SUM(TP.VALOR_EXTRA) AS VALOR_EXTRA,
        SUM(TP.VALOR_FREELA) AS VALOR_FREELA,
        SUM(TP.VALOR_TAXA_ESTAFF) AS VALOR_ESTAFF, -- FATURAMENTO DA STAFF
        SUM(TP.VALOR_BRUTO) AS VALOR_BRUTO_P,  -- Novo alias para diferenciar
        0 AS VALOR_BRUTO_E,  -- Garante que eventos terão 0 aqui
        0 AS NUM_EVENTOS,
        0 AS VALOR_LIQUIDO,
        0 AS TAXA_EVENTO,
        0 AS VALOR_CONTRATO,
  			TC.NAME AS COMPANIE,
  			TCG.NOME AS GROUP_COMPANIE
    FROM T_PROPOSALS TP 
    INNER JOIN T_PROPOSAL_STATUS TPS ON TP.FK_PROPOSAL_STATUS = TPS.ID
    INNER JOIN T_FREELA TF ON TP.FK_FREELA = TF.ID
    INNER JOIN ADMIN_USERS AU ON TF.FK_ADMIN_USERS = AU.ID
    INNER JOIN T_OPPORTUNITIES TO2 ON TP.FK_OPPORTUNITIE = TO2.ID
    INNER JOIN T_COMPANIES TC ON TO2.FK_COMPANIE = TC.ID
    INNER JOIN T_PROPOSAL_TYPE TPT ON TO2.FK_PROPOSAL_TYPE = TPT.ID
    LEFT JOIN T_STATUS_PAGAMENTO TSP ON TP.FK_STATUS_PAGAMENTO = TSP.ID
    LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
    WHERE TP.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
    AND TC.ID NOT IN (111)
    AND (TC.FK_GROUP IS NULL OR TC.FK_GROUP <> 113)                                
  	{filters}
	GROUP BY YEAR(TO2.START_AT), MONTH(TO2.START_AT)
),
    
EVENTOS AS (
    SELECT
        DATE_FORMAT(TEE.DATA_INICIO_EVENTO, '%m/%Y') AS DATA,
        0 AS NUM_JOBS_B2B,
        0 AS VALOR_OPORTUNIDADE,
        0 AS VALOR_EXTRA,
        0 AS VALOR_FREELA,
        0 AS VALOR_ESTAFF,
        0 AS VALOR_BRUTO_P,  -- Garante que propostas terão 0 aqui
        SUM(TEE.VALOR_BRUTO) AS VALOR_BRUTO_E,  -- Novo alias para diferenciar
        COUNT(TEE.ID) AS NUM_EVENTOS,
        SUM(TEE.VALOR_LIQUIDO) AS VALOR_LIQUIDO,
        (SUM(TEE.VALOR_BRUTO) - SUM(TEE.VALOR_LIQUIDO)) AS TAXA_EVENTO,
        0 AS VALOR_CONTRATO,
  			TC.NAME AS COMPANIE,
  			TCG.NOME AS GROUP_COMPANIE
    FROM T_EVENTOS_EXTERNOS TEE
    LEFT JOIN T_COMPANIES TC ON TEE.FK_COMPANIE = TC.ID
  	LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
  	WHERE 1=1
    {filters}
    GROUP BY TEE.DATA_INICIO_EVENTO
),
Parcela AS (
    SELECT 1 AS num UNION ALL
    SELECT 2 UNION ALL
    SELECT 3 UNION ALL
    SELECT 4 UNION ALL
    SELECT 5
),

BRIGADA AS (
    SELECT
        DATE_FORMAT(
            CASE P.num 
                WHEN 1 THEN BF.DATA_VENCIMENTO_PARCELA_1
                WHEN 2 THEN BF.DATA_VENCIMENTO_PARCELA_2
                WHEN 3 THEN BF.DATA_VENCIMENTO_PARCELA_3
                WHEN 4 THEN BF.DATA_VENCIMENTO_PARCELA_4
                WHEN 5 THEN BF.DATA_VENCIMENTO_PARCELA_5 
            END, '%m/%Y'
        ) AS DATA,
        0 AS NUM_JOBS_B2B,
        0 AS VALOR_OPORTUNIDADE,
        0 AS VALOR_EXTRA,
        0 AS VALOR_FREELA,
        0 AS VALOR_ESTAFF,
        0 AS VALOR_BRUTO_P,
        0 AS VALOR_BRUTO_E,
        0 AS NUM_EVENTOS,
        0 AS VALOR_LIQUIDO,
        0 AS TAXA_EVENTO,
        SUM(CASE P.num 
            WHEN 1 THEN BF.VALOR_PARCELA_1
            WHEN 2 THEN BF.VALOR_PARCELA_2
            WHEN 3 THEN BF.VALOR_PARCELA_3
            WHEN 4 THEN BF.VALOR_PARCELA_4
            WHEN 5 THEN BF.VALOR_PARCELA_5 
        END) AS VALOR_CONTRATO,
  	TC.NAME AS COMPANIE,
  	TCG.NOME AS GROUP_COMPANIE
    FROM T_BRIGADA_FIXA BF
    LEFT JOIN T_COMPANIES TC ON BF.FK_COMPANIES = TC.ID
  	LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
    CROSS JOIN Parcela P
    WHERE BF.STATUS <> 101
  	{filters}
    AND CASE P.num 
        WHEN 1 THEN BF.DATA_VENCIMENTO_PARCELA_1
        WHEN 2 THEN BF.DATA_VENCIMENTO_PARCELA_2
        WHEN 3 THEN BF.DATA_VENCIMENTO_PARCELA_3
        WHEN 4 THEN BF.DATA_VENCIMENTO_PARCELA_4
        WHEN 5 THEN BF.DATA_VENCIMENTO_PARCELA_5 
    END IS NOT NULL
    GROUP BY DATA
)
SELECT 
    DATA AS 'Mês/Ano',
    SUM(NUM_JOBS_B2B) AS 'Num. Jobs B2B',
    SUM(VALOR_BRUTO_P) AS 'Valor Bruto B2B',
    SUM(VALOR_ESTAFF) AS 'Taxa B2B',
    SUM(VALOR_OPORTUNIDADE) AS 'Total Oportunidade',
    SUM(VALOR_EXTRA) AS 'Total Extra',
    SUM(VALOR_FREELA) AS 'Valor Freela',
    SUM(NUM_EVENTOS) AS 'Num. Eventos',
    SUM(VALOR_BRUTO_E) AS 'Valor Transac. Eventos',
    SUM(TAXA_EVENTO) AS 'Taxa Eventos',
    SUM(VALOR_CONTRATO) AS 'Taxa Brigada Fixa',
    (SUM(VALOR_ESTAFF) + SUM(TAXA_EVENTO) + SUM(VALOR_CONTRATO)) AS 'Faturamento Total'
FROM (
    SELECT * FROM PROPOLS
    UNION ALL
    SELECT * FROM EVENTOS
    UNION ALL
    SELECT * FROM BRIGADA
) AS COMBINED
WHERE STR_TO_DATE(CONCAT('01/', DATA), '%d/%m/%Y') >= '{day1}'
AND STR_TO_DATE(CONCAT('01/', DATA), '%d/%m/%Y') <= '{day2}'
GROUP BY DATA
ORDER BY STR_TO_DATE(CONCAT('01/', DATA), '%d/%m/%Y') ASC;
""")

@st.cache_data
def estabelecimento_transaction(day1, day2):
    return get_dataframe_from_query(f"""
SELECT 
C.NAME as 'Estabelecimento',
COUNT(P.ID) as 'Num. Jobs',
SUM(P.VALOR_BRUTO) as 'Valor Transac.'

FROM T_PROPOSALS P 
INNER JOIN T_PROPOSAL_STATUS PS ON (P.FK_PROPOSAL_STATUS = PS.ID)
INNER JOIN T_OPPORTUNITIES O ON (O.ID = P.FK_OPPORTUNITIE)
INNER JOIN T_COMPANIES C ON (O.FK_COMPANIE = C.ID)
INNER JOIN T_PROPOSAL_TYPE PT ON (O.FK_PROPOSAL_TYPE = PT.ID)
WHERE P.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
AND C.ID NOT IN (111, 138, 143) 
AND O.START_AT >= '{day1} 00:00:00'
AND O.START_AT <= '{day2} 23:59:59'
AND (C.FK_GROUP IS NULL OR C.FK_GROUP <> 113)
GROUP BY C.NAME

ORDER BY COUNT(P.ID) DESC
""")

@st.cache_data
def groups_companies(day1 , day2):
    return get_dataframe_from_query(f"""
WITH PROPOLS AS (
    SELECT
        DATE_FORMAT(TO2.START_AT, '%m/%Y') AS DATA,
  			TC.NAME AS COMPANIE,
  			TCG.NOME AS GROUP_COMPANIE
    FROM T_PROPOSALS TP 
    INNER JOIN T_PROPOSAL_STATUS TPS ON TP.FK_PROPOSAL_STATUS = TPS.ID
    INNER JOIN T_FREELA TF ON TP.FK_FREELA = TF.ID
    INNER JOIN ADMIN_USERS AU ON TF.FK_ADMIN_USERS = AU.ID
    INNER JOIN T_OPPORTUNITIES TO2 ON TP.FK_OPPORTUNITIE = TO2.ID
    INNER JOIN T_COMPANIES TC ON TO2.FK_COMPANIE = TC.ID
    INNER JOIN T_PROPOSAL_TYPE TPT ON TO2.FK_PROPOSAL_TYPE = TPT.ID
    LEFT JOIN T_STATUS_PAGAMENTO TSP ON TP.FK_STATUS_PAGAMENTO = TSP.ID
    LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
    WHERE TP.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
    AND (TC.FK_GROUP IS NULL OR TC.FK_GROUP <> 113)
    AND TC.ID NOT IN (111)
	GROUP BY TO2.START_AT
),
    
EVENTOS AS (
    SELECT
        DATE_FORMAT(TEE.DATA_INICIO_EVENTO, '%m/%Y') AS DATA,
  			TC.NAME AS COMPANIE,
  			TCG.NOME AS GROUP_COMPANIE
    FROM T_EVENTOS_EXTERNOS TEE
    LEFT JOIN T_COMPANIES TC ON TEE.FK_COMPANIE = TC.ID
  	LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
  	WHERE 1=1
    GROUP BY TEE.DATA_INICIO_EVENTO
),
Parcela AS (
    SELECT 1 AS num UNION ALL
    SELECT 2 UNION ALL
    SELECT 3 UNION ALL
    SELECT 4 UNION ALL
    SELECT 5
),

BRIGADA AS (
    SELECT
        DATE_FORMAT(
            CASE P.num 
                WHEN 1 THEN BF.DATA_VENCIMENTO_PARCELA_1
                WHEN 2 THEN BF.DATA_VENCIMENTO_PARCELA_2
                WHEN 3 THEN BF.DATA_VENCIMENTO_PARCELA_3
                WHEN 4 THEN BF.DATA_VENCIMENTO_PARCELA_4
                WHEN 5 THEN BF.DATA_VENCIMENTO_PARCELA_5 
            END, '%m/%Y'
        ) AS DATA,
        
  	TC.NAME AS COMPANIE,
  	TCG.NOME AS GROUP_COMPANIE
    FROM T_BRIGADA_FIXA BF
    LEFT JOIN T_COMPANIES TC ON BF.FK_COMPANIES = TC.ID
  	LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
    CROSS JOIN Parcela P
    WHERE BF.STATUS <> 101
    AND CASE P.num 
        WHEN 1 THEN BF.DATA_VENCIMENTO_PARCELA_1
        WHEN 2 THEN BF.DATA_VENCIMENTO_PARCELA_2
        WHEN 3 THEN BF.DATA_VENCIMENTO_PARCELA_3
        WHEN 4 THEN BF.DATA_VENCIMENTO_PARCELA_4
        WHEN 5 THEN BF.DATA_VENCIMENTO_PARCELA_5 
    END IS NOT NULL
    GROUP BY DATA
)
SELECT 
    COMPANIE AS 'ESTABELECIMENTO',
    GROUP_COMPANIE AS 'GRUPO'
FROM (
    SELECT * FROM PROPOLS
    UNION ALL
    SELECT * FROM EVENTOS
    UNION ALL
    SELECT * FROM BRIGADA
) AS COMBINED
WHERE STR_TO_DATE(CONCAT('01/', DATA), '%d/%m/%Y') >= '{day1}'
AND STR_TO_DATE(CONCAT('01/', DATA), '%d/%m/%Y') <= '{day2}'
GROUP BY COMPANIE, GROUP_COMPANIE
ORDER BY STR_TO_DATE(CONCAT('01/', DATA), '%d/%m/%Y') ASC
""")

@st.cache_data
def general_revenue_oportunity(day1, day2, filters):
    return get_dataframe_from_query(f"""
    SELECT
    	TO2.ID AS 'ID OPORTUNIDADE',
    	TP.ID AS 'ID PROPOSTA',
        TC.NAME AS 'ESTABELECIMENTO',
        TC.ID AS 'ID ESTABELECIMENTO',
        TC.UF AS 'UF',
        TC.CITY AS 'CIDADE',
        DATE_FORMAT(TO2.START_AT, '%d/%m/%Y') AS DATA,
        TP.DATA_PAGAMENTO AS 'PAGAMENTO',
        TF.NOME_SOCIAL AS 'FREELA',
        TP.VALOR_BRUTO AS 'VALOR BRUTO P',
        TO2.VALUE AS 'VALOR OPORTUNIDADE',
        TP.VALOR_EXTRA AS 'VALOR EXTRA',
        TP.VALOR_FREELA AS 'VALOR FREELA',
        TP.VALOR_TAXA_ESTAFF AS 'VALOR STAFF'
    FROM T_PROPOSALS TP 
    INNER JOIN T_PROPOSAL_STATUS TPS ON TP.FK_PROPOSAL_STATUS = TPS.ID
    INNER JOIN T_FREELA TF ON TP.FK_FREELA = TF.ID
    INNER JOIN ADMIN_USERS AU ON TF.FK_ADMIN_USERS = AU.ID
    INNER JOIN T_OPPORTUNITIES TO2 ON TP.FK_OPPORTUNITIE = TO2.ID
    INNER JOIN T_COMPANIES TC ON TO2.FK_COMPANIE = TC.ID
    INNER JOIN T_PROPOSAL_TYPE TPT ON TO2.FK_PROPOSAL_TYPE = TPT.ID
    LEFT JOIN T_STATUS_PAGAMENTO TSP ON TP.FK_STATUS_PAGAMENTO = TSP.ID
    LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
    WHERE TP.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
    AND TC.ID NOT IN (111)
    AND TO2.START_AT >= '{day1} 00:00:00'
    AND TO2.START_AT <= '{day2} 23:59:59'
    AND (TC.FK_GROUP IS NULL OR TC.FK_GROUP <> 113)
    {filters}
    ORDER BY TO2.START_AT
""")

@st.cache_data
def general_revenue_events(day1, day2, filters):
    return get_dataframe_from_query(f"""
SELECT
  TEE.ID AS 'ID EVENTO',
  TEE.NOME_EVENTO AS 'EVENTO',
  TC.NAME AS 'ESTABELECIMENTO',
  TC.ID AS 'ID ESTABELECIMENTO',
  TC.UF AS 'UF',
  TC.CITY AS 'CIDADE',
  DATE_FORMAT(TEE.DATA_INICIO_EVENTO, '%d/%m/%Y') AS DATA,
  TEE.DATA_PAGAMENTO AS 'PAGAMENTO',
  TEE.VALOR_BRUTO AS 'VALOR BRUTO',
  TEE.VALOR_LIQUIDO AS 'VALOR LIQUIDO',
  TEE.CUSTOS_EXTRAS_EVENTOS AS 'CUSTO EXTRA',
  (TEE.VALOR_BRUTO - TEE.VALOR_LIQUIDO) AS 'TAXA EVENTO'
FROM T_EVENTOS_EXTERNOS TEE
LEFT JOIN T_COMPANIES TC ON TEE.FK_COMPANIE = TC.ID 
LEFT JOIN T_COMPANY_GROUP TCG ON TC.FK_GROUP = TCG.ID
WHERE TEE.DATA_INICIO_EVENTO >= '{day1}'
AND TEE.DATA_INICIO_EVENTO <= '{day2}'
{filters}
ORDER BY TEE.DATA_INICIO_EVENTO                                 
""")

@st.cache_data
def general_revenue_brigada(day1, day2, filters):
    return get_dataframe_from_query(f"""
SELECT
    BF.ID AS 'ID BRIGADA',
    BF.NOME_CONTRATO AS 'CONTRATO',
  	C.NAME AS 'ESTABELECIMENTO',
    C.ID AS 'ID ESTABELECIMENTO',
    C.UF AS 'UF',
   	C.CITY AS 'CIDADE',
    DATE_FORMAT(BF.DATA_INICIO_CONTRATO, '%d/%m/%Y') AS 'INICIO CONTRATO',
    DATE_FORMAT(BF.DATA_FIM_CONTRATO, '%d/%m/%Y') AS 'FIM CONTRATO',
    BF.VALOR_CONTRATO AS 'VALOR CONTRATO',
    BF.VALOR_PARCELA_1 AS 'PARCELA 1',
    DATE_FORMAT(BF.DATA_VENCIMENTO_PARCELA_1, '%d/%m/%Y') AS 'VENCIMENTO PARCELA 1',
    BF.VALOR_PARCELA_2 AS 'PARCELA 2',
    DATE_FORMAT(BF.DATA_VENCIMENTO_PARCELA_2, '%d/%m/%Y') AS 'VENCIMENTO PARCELA 2',
    BF.VALOR_PARCELA_3 AS 'PARCELA 3',
    DATE_FORMAT(BF.DATA_VENCIMENTO_PARCELA_3, '%d/%m/%Y') AS 'VENCIMENTO PARCELA 3',
    BF.VALOR_PARCELA_4 AS 'PARCELA 4',
    DATE_FORMAT(BF.DATA_VENCIMENTO_PARCELA_4, '%d/%m/%Y') AS 'VENCIMENTO PARCELA 4',
    BF.VALOR_PARCELA_5 AS 'PARCELA 5',
    DATE_FORMAT(BF.DATA_VENCIMENTO_PARCELA_5, '%d/%m/%Y') AS 'VENCIMENTO PARCELA 5'
FROM T_BRIGADA_FIXA BF
LEFT JOIN T_COMPANIES C ON BF.FK_COMPANIES = C.ID
LEFT JOIN T_COMPANY_GROUP TCG ON C.FK_GROUP = TCG.ID
WHERE BF.STATUS <> 101
AND (
    (BF.DATA_VENCIMENTO_PARCELA_1 BETWEEN '{day1}' AND '{day2}') OR
    (BF.DATA_VENCIMENTO_PARCELA_2 BETWEEN '{day1}' AND '{day2}') OR
    (BF.DATA_VENCIMENTO_PARCELA_3 BETWEEN '{day1}' AND '{day2}') OR
    (BF.DATA_VENCIMENTO_PARCELA_4 BETWEEN '{day1}' AND '{day2}') OR
    (BF.DATA_VENCIMENTO_PARCELA_5 BETWEEN '{day1}' AND '{day2}')
)
{filters}
ORDER BY 
    COALESCE(BF.DATA_VENCIMENTO_PARCELA_1, BF.DATA_VENCIMENTO_PARCELA_2, BF.DATA_VENCIMENTO_PARCELA_3, BF.DATA_VENCIMENTO_PARCELA_4, BF.DATA_VENCIMENTO_PARCELA_5)
""")

@st.cache_data
def billing_companies(day1, day2):
    return get_dataframe_from_query(f"""
SELECT 
C.NAME AS 'Estabelecimento',
COUNT(P.ID) AS 'NÚM. DE TRABALHOS',
COUNT(DISTINCT(PT.TYPE)) AS 'FUNÇÕES DISTINTAS',
COUNT(DISTINCT(AU.FULL_NAME)) AS 'FREELAS DISTINTOS',
SUM(P.VALOR_BRUTO) AS 'VALOR TRANSACIONADO',
SUM(P.VALOR_TAXA_ESTAFF) AS 'TAXA ESTAFF',
SUM(O.VALUE) AS 'VALOR LIQUIDO',
SUM(P.VALOR_EXTRA) AS 'VALOR EXTRA',
SUM(P.VALOR_FREELA) AS 'VALOR FREELA',
SUM(P.VALOR_BRUTO) AS 'VALOR BRUTO'
FROM T_PROPOSALS P 
INNER JOIN T_PROPOSAL_STATUS PS ON (P.FK_PROPOSAL_STATUS = PS.ID)
INNER JOIN T_FREELA F ON (P.FK_FREELA = F.ID)
INNER JOIN ADMIN_USERS AU ON (F.FK_ADMIN_USERS = AU.ID)
INNER JOIN T_OPPORTUNITIES O ON (O.ID = P.FK_OPPORTUNITIE)
INNER JOIN T_COMPANIES C ON (O.FK_COMPANIE = C.ID)
INNER JOIN T_PROPOSAL_TYPE PT ON (O.FK_PROPOSAL_TYPE = PT.ID)
LEFT JOIN T_KEY_ACCOUNTS KA ON (KA.ID = C.FK_KEY_ACCOUNT)
LEFT JOIN T_COMPANY_GROUP CG ON (CG.ID = C.FK_GROUP)
WHERE P.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
AND C.ID NOT IN (111, 138, 143)
AND O.START_AT > '2022-12-31 23:59:59'
AND O.START_AT >= '{day1} 00:00:00'
AND O.START_AT <= '{day2} 23:59:59'
AND (C.FK_GROUP IS NULL OR C.FK_GROUP <> 113)
GROUP BY C.NAME
ORDER BY SUM(P.VALOR_TAXA_ESTAFF) DESC
""")

@st.cache_data
def works_by_functions(day1, day2):
    return get_dataframe_from_query(f"""
SELECT 
PT.TYPE AS 'FUNÇÃO',
CASE 
  WHEN SUM(TIMESTAMPDIFF(HOUR, O.START_AT, O.END_AD)) > 0 
  THEN ROUND(SUM(O.VALUE) / SUM(TIMESTAMPDIFF(HOUR, O.START_AT, O.END_AD)), 2) 
  ELSE 0 
END AS 'VALOR MÉDIO POR HORA',

CASE 
WHEN COUNT(P.ID) > 0 
THEN ROUND(SUM(TIMESTAMPDIFF(HOUR, O.START_AT, O.END_AD)) / COUNT(P.ID), 2) 
ELSE 0 
END AS 'JORNADA MEDIA (HORAS)',

COUNT(DISTINCT(AU.FULL_NAME)) AS 'FREELAS DISTINTOS',
COUNT(P.ID) AS 'NÚM. DE TRABALHOS'

FROM T_PROPOSALS P 
INNER JOIN T_PROPOSAL_STATUS PS ON (P.FK_PROPOSAL_STATUS = PS.ID)
INNER JOIN T_FREELA F ON (P.FK_FREELA = F.ID)
INNER JOIN ADMIN_USERS AU ON (F.FK_ADMIN_USERS = AU.ID)
INNER JOIN T_OPPORTUNITIES O ON (O.ID = P.FK_OPPORTUNITIE)
INNER JOIN T_COMPANIES C ON (O.FK_COMPANIE = C.ID)
INNER JOIN T_PROPOSAL_TYPE PT ON (O.FK_PROPOSAL_TYPE = PT.ID)
LEFT JOIN T_KEY_ACCOUNTS KA ON (KA.ID = C.FK_KEY_ACCOUNT)
LEFT JOIN T_COMPANY_GROUP CG ON (CG.ID = C.FK_GROUP)
WHERE P.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
AND C.ID NOT IN (111, 138, 143)
AND O.START_AT > '2022-12-31 23:59:59'
AND O.START_AT >= '{day1} 00:00:00'
AND O.START_AT <= '{day2} 23:59:59'
AND (C.FK_GROUP IS NULL OR C.FK_GROUP <> 113)
GROUP BY PT.TYPE
ORDER BY COUNT(P.ID) DESC
""")

@st.cache_data
def average_freela_value_and_hourly_rate(day1, day2):
    return get_dataframe_from_query(f"""
SELECT 
COUNT(DISTINCT(F.ID)) AS 'FREELAS DISTINTOS',
SUM(O.VALUE) / COUNT(F.ID) AS 'VALOR MEDIO POR JOB',
SUM(O.VALUE) / SUM(TIMESTAMPDIFF(HOUR, O.START_AT, O.END_AD)) AS 'VALOR MEDIO POR HORA'

FROM T_PROPOSALS P 
INNER JOIN T_PROPOSAL_STATUS PS ON (P.FK_PROPOSAL_STATUS = PS.ID)
INNER JOIN T_FREELA F ON (P.FK_FREELA = F.ID)
INNER JOIN ADMIN_USERS AU ON (F.FK_ADMIN_USERS = AU.ID)
INNER JOIN T_OPPORTUNITIES O ON (O.ID = P.FK_OPPORTUNITIE)
INNER JOIN T_COMPANIES C ON (O.FK_COMPANIE = C.ID)
INNER JOIN T_PROPOSAL_TYPE PT ON (O.FK_PROPOSAL_TYPE = PT.ID)
LEFT JOIN T_KEY_ACCOUNTS KA ON (KA.ID = C.FK_KEY_ACCOUNT)
LEFT JOIN T_COMPANY_GROUP CG ON (CG.ID = C.FK_GROUP)
WHERE P.FK_PROPOSAL_STATUS IN (102, 103, 106, 115)
AND C.ID NOT IN (111, 138, 143)
AND O.START_AT > '2022-12-31 23:59:59'
AND O.START_AT >= '{day1} 00:00:00'
AND O.START_AT <= '{day2} 23:59:59'
AND (C.FK_GROUP IS NULL OR C.FK_GROUP <> 113)
""")