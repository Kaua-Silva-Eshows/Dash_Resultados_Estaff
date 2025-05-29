import mysql.connector
import streamlit as st
import pandas as pd

def get_mysql_connection_eshows():
    mysql_config = st.secrets["mysql_eshows"]
    # Create MySQL connection
    conn = mysql.connector.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        user=mysql_config['username'],
        password=mysql_config['password']
    )    
    return conn

def get_mysql_connection_fabrica():
    mysql_config = st.secrets["mysql_fabrica"]
    # Create MySQL connection
    conn = mysql.connector.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        user=mysql_config['username'],
        password=mysql_config['password']    
    )    
    return conn

def execute_query(query, use_fabrica=False):
    conn = (
    get_mysql_connection_fabrica() if use_fabrica 
    else get_mysql_connection_eshows()
)

    cursor = conn.cursor()
    try:
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
        
        cursor.execute(query)
        
        # Verifique se cursor.description não é None
        if cursor.description is None:
            print("Descrição do cursor é None")
            return None, None

        # Obter nomes das colunas
        column_names = [col[0] for col in cursor.description]
        
        # Obter resultados
        result = cursor.fetchall()
        
        if not result:
            print("Nenhuma linha retornada pela consulta.")
        
        cursor.close()
        conn.close()
        return result, column_names
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def get_dataframe_from_query(consulta, use_fabrica=False):
    result, column_names = execute_query(consulta, use_fabrica)
    if result is None or column_names is None:
        return pd.DataFrame() 
    return pd.DataFrame(result, columns=column_names)

