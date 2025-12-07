from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator # <--- Nova ferramenta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
from minio import Minio
import os

# --- CONFIGURAÇÕES ---
MINIO_ENDPOINT = "minio:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "landing-zone"
ARQUIVO_NOME = "vendas_perfumaria.csv"

# --- FUNÇÕES ---

def gerar_dados_fake():
    """Gera CSV fake e salva na pasta temporária"""
    dados = {
        "id_pedido": [101, 102, 103, 104, 105, 106, 107],
        "cliente": ["Ana", "Bruno", "Carla", "Daniel", "Elisa", "Fabio", "Gabriela"],
        "produto": ["Malbec", "Lily Essence", "Egeo Choc", "Malbec", "Glamour", "Coffee Woman", "Accord"],
        "categoria": ["Perfumaria", "Perfumaria", "Perfumaria", "Perfumaria", "Perfumaria", "Perfumaria", "Perfumaria"],
        "valor": [189.90, 249.90, 119.90, 189.90, 159.90, 169.90, 199.90],
        "data_venda": ["2025-07-01", "2025-07-01", "2025-07-02", "2025-07-03", "2025-07-03", "2025-07-04", "2025-07-04"],
        "status_entrega": ["Entregue", "Atrasado", "Entregue", "Em Trânsito", "Cancelado", "Entregue", "Atrasado"]
    }
    
    df = pd.DataFrame(dados)
    caminho = f"/tmp/{ARQUIVO_NOME}"
    df.to_csv(caminho, index=False)
    return caminho

def upload_para_minio():
    """Envia do local para o MinIO"""
    client = Minio(MINIO_ENDPOINT, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
    client.fput_object(BUCKET_NAME, ARQUIVO_NOME, f"/tmp/{ARQUIVO_NOME}")

def transferir_para_postgres():
    """Lê do MinIO e salva na Camada Bronze"""
    client = Minio(MINIO_ENDPOINT, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
    obj = client.get_object(BUCKET_NAME, ARQUIVO_NOME)
    df = pd.read_csv(obj)
    
    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    engine = pg_hook.get_sqlalchemy_engine()
    df.to_sql('vendas_bronze', engine, if_exists='replace', index=False)

# --- DAG ---

with DAG(
    dag_id="03_pipeline_boticario_final", # Nome final
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    # Passo 1: Python cria os dados
    t1 = PythonOperator(task_id="gerar_dados", python_callable=gerar_dados_fake)
    
    # Passo 2: Python joga no Data Lake
    t2 = PythonOperator(task_id="upload_minio", python_callable=upload_para_minio)
    
    # Passo 3: Python joga no Data Warehouse (Raw)
    t3 = PythonOperator(task_id="ingestao_postgres", python_callable=transferir_para_postgres)

    # Passo 4: dbt transforma os dados (Raw -> Analytics)
    # Aqui usamos BashOperator porque o dbt é um comando de terminal
    t4 = BashOperator(
        task_id="transformacao_dbt",
        bash_command="dbt run --project-dir /opt/airflow/dags/transformacao_dbt --profiles-dir /opt/airflow/dags/transformacao_dbt"
    )

    # A ordem dos tratores
    t1 >> t2 >> t3 >> t4