import pandas as pd
from sqlalchemy import create_engine
import time
import os

print("Iniciando script de ETL...")

# --- 1. Conexão com o Banco de Dados ---

DB_USER = "challenge"
DB_PASSWORD = "challenge_2024"
DB_HOST_DOCKER = "postgres"  
DB_HOST_LOCAL = "localhost"
DB_PORT = "5432"
DB_NAME = "challenge_db"

# String de conexão
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST_LOCAL}:{DB_PORT}/{DB_NAME}")

# Criar engine de conexão

try:
    engine = create_engine(DATABASE_URL)
    print("Conexão com o banco de dados estabelecida.")

except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    exit()

# --- 2. Extração dos Dados ---

try:
    query = "SELECT * FROM sales;"
    df = pd.read_sql(query, engine)
    print("Dados extraídos com sucesso.")

except Exception as e:
    print(f"Erro ao extrair dados: {e}")
    exit()


# --- 3. A Query SQL (O Coração do ETL) ---


SQL_QUERY = """
SELECT 
    sales.id AS venda_id,
    sales.created_at AS data_venda,
    sales.total_amount AS valor_total_venda,
    sales.total_discount AS desconto_venda,
    sales.delivery_fee AS taxa_entrega,
    sales.sale_status_desc AS status_venda,
    sales.production_seconds AS tempo_preparo_seg,
    sales.delivery_seconds AS tempo_entrega_seg,

    stores.name AS loja_nome,
    stores.city AS loja_cidade,

    channels.name AS canal_nome,

    products.name AS produto_nome,
    categories.name AS produto_categoria,

    product_sales.quantity AS produto_qtde,
    product_sales.total_price AS produto_valor_total,

    delivery.neighborhood AS bairro_entrega,
    delivery.city AS cidade_entrega

FROM 
    sales 
JOIN 
    stores ON sales.store_id = stores.id
JOIN 
    channels ON sales.channel_id = channels.id
JOIN 
    product_sales ON product_sales.sale_id = sales.id
JOIN 
    products ON product_sales.product_id = products.id
JOIN 
    categories ON products.category_id = categories.id
LEFT JOIN 
    delivery_addresses as delivery ON sales.id = delivery.sale_id
WHERE
    sales.sale_status_desc = 'COMPLETED'; -- Focamos apenas em vendas completas
"""

# --- 4. Execução e Carregamento (Extract & Transform) ---

print("Iniciando a extração de dados... Isso pode levar alguns minutos.")
start_time = time.time()

try:
    
    df = pd.read_sql(SQL_QUERY, engine)
    
    elapsed = time.time() - start_time
    print(f"Dados extraídos com sucesso em {elapsed:.2f} segundos.")
    print(f"Total de linhas (produtos vendidos): {len(df)}")

except Exception as e:
    print(f"Erro ao executar a query SQL: {e}")
    exit()

# --- 5. Load ---


OUTPUT_FILE = "dados_analiticos.parquet"

print(f"Salvando dados transformados em '{OUTPUT_FILE}'...")
start_time = time.time()

try:
    df.to_parquet(OUTPUT_FILE, index=False, engine='pyarrow')
    
    elapsed = time.time() - start_time
    print(f"Arquivo Parquet salvo com sucesso em {elapsed:.2f} segundos.")
    print("\n--- Processo de ETL concluído! ---")
    print(f"Agora você pode usar o arquivo '{OUTPUT_FILE}' no seu Streamlit.")

except Exception as e:
    print(f"Erro ao salvar o arquivo Parquet: {e}")

    exit()


    




