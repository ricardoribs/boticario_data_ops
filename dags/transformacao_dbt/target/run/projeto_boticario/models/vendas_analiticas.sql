
  
    

  create  table "airflow"."public"."vendas_analiticas__dbt_tmp"
  
  
    as
  
  (
    /*
    Aqui pegamos a tabela bruta que o Python criou (vendas_bronze)
    e aplicamos regras de negócio.
*/

WITH vendas_brutas AS (
    -- O dbt recomenda usar 'source' ou 'ref', mas vamos simplificar usando o nome direto
    SELECT * FROM public.vendas_bronze
)

SELECT
    id_pedido,
    cliente,
    produto,
    categoria,
    valor,
    data_venda,
    status_entrega,
    -- Regra de Negócio 1: Categorizar valor do pedido
    CASE 
        WHEN valor > 200 THEN 'Premium'
        WHEN valor > 150 THEN 'Padrão'
        ELSE 'Básico'
    END AS classe_pedido,
    -- Regra de Negócio 2: Flag de problema logístico (Isso o Boticário ama)
    CASE 
        WHEN status_entrega IN ('Atrasado', 'Cancelado') THEN true
        ELSE false
    END AS teve_problema
FROM vendas_brutas
  );
  