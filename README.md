# 💄 Beauty Retail Lakehouse: End-to-End Data Engineering

![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Airflow](https://img.shields.io/badge/Orchestration-Apache%20Airflow-blue?style=for-the-badge&logo=apacheairflow)
![dbt](https://img.shields.io/badge/Transformation-dbt%20Core-orange?style=for-the-badge&logo=dbt)
![Docker](https://img.shields.io/badge/Infrastructure-Docker-2496ED?style=for-the-badge&logo=docker)
![Postgres](https://img.shields.io/badge/Warehouse-PostgreSQL-336791?style=for-the-badge&logo=postgresql)

> **Business Case:** Construção de uma arquitetura de dados escalável para monitoramento de KPIs logísticos e classificação de vendas em um e-commerce de beleza.

---

## 📋 Sobre o Projeto

Este projeto simula um desafio real de engenharia de dados no varejo (inspirado no cenário do **Grupo Boticário**). O objetivo foi sair de scripts manuais e construir uma **Modern Data Stack** completa, containerizada e automatizada.

O pipeline resolve o problema de **descentralização de dados**, ingerindo transações brutas, armazenando-as em um Data Lake e transformando-as em tabelas analíticas confiáveis para o time de negócios acompanhar **atrasos de entrega** e **ticket médio por cliente**.

---

## 🏗️ Arquitetura (Lakehouse)

A solução segue a arquitetura de **Medalhão (Bronze, Silver, Gold)**, garantindo rastreabilidade e qualidade do dado.

graph LR

    subgraph Ingestao
        A["Gerador de Vendas\n(Python Script)"] -->|Raw CSV| B["MinIO\n(Data Lake)"]
    end

    subgraph Warehousing
        B -->|Copy| C["PostgreSQL\nCamada Bronze"]
    end

    subgraph Transformacao
        C -->|dbt run| D["dbt Core"]
        D -->|SQL + Testes| E["PostgreSQL\nCamada Gold"]
    end

    style A fill:#f9f,stroke:#333
    style B fill:#add8e6,stroke:#333
    style D fill:#ff4500,color:white,stroke:#333
    style E fill:#90ee90,stroke:#333


🛠️ Decisões Técnicas (Tech Stack)

Componente	Tecnologia	Por que escolhi?
Orquestração	Apache Airflow	Para gerenciar dependências complexas e retries automáticos. O código é definido como DAGs (Python), facilitando versionamento.
Data Lake	MinIO	        Simula o AWS S3 localmente. Permite desacoplar o armazenamento (barato) do processamento.
Transformação	dbt Core	Traz as boas práticas de engenharia de software (testes, modularidade, git) para o SQL.
Infraestrutura	Docker Compose	Garante que o ambiente seja reprodutível em qualquer máquina (Infrastructure as Code).
Warehouse	PostgreSQL	Banco robusto para servir a camada analítica final.

⚙️ O Pipeline Detalhado
O fluxo é controlado pela DAG 03_pipeline_boticario_final, que executa as seguintes etapas sequenciais:

1. Extract (Python): Simulação de geração de dados transacionais com variação de cenários (pedidos cancelados, atrasados, etc).

2. Load to Lake (MinIO): O arquivo é persistido no bucket landing-zone. Isso garante que, se o banco cair, o dado bruto está salvo (Disaster Recovery).

3. Load to DW (Postgres): Carregamento da tabela vendas_bronze (Raw).

4. Transform (dbt): * Limpeza de tipos de dados.

 • Criação da regra de negócio classe_pedido (Premium/Padrão).

 • Criação da flag teve_problema para monitoramento de SLA logístico.

📸 Evidências

1. Orquestração com Sucesso (Airflow)
O pipeline completo rodando sem intervenção manual.

![Fluxo Airflow](./airflow_graph.png)

2. Modelo de Dados Final (Analítico)
A tabela final pronta para ser consumida por ferramentas de BI (Power BI/Metabase).

![Terminal SQL](./resultado_final.png)

📂 Estrutura do Repositório
boticario_data_ops/
├── dags/
│   ├── transformacao_dbt/  # Projeto dbt isolado
│   │   ├── models/         # Regras de negócio SQL
│   │   └── dbt_project.yml
│   └── pipeline_ingestao.py # A DAG do Airflow
├── data/                    # Persistência local do MinIO
├── Dockerfile               # Customização da imagem Airflow
├── docker-compose.yaml      # Orquestração dos containers
└── README.md

🚀 Como Executar
Pré-requisitos: Docker e Docker Compose instalados.
1. Clone o repositório:
git clone [https://github.com/ricardoribs/boticario_data_ops.git](https://github.com/ricardoribs/boticario_data_ops.git)
cd boticario_data_ops

2. Suba o ambiente:
docker-compose up -d --build

3. Acesse as interfaces:
 • Airflow: http://localhost:8080 (User/Pass: airflow)

 • MinIO: http://localhost:9001 (User/Pass: minioadmin)

4. Execute: Ative a DAG 03_pipeline_boticario_final e acompanhe o fluxo ficar verde!

🔮 Próximos Passos (Melhorias)
 • [ ] Implementar Great Expectations para validação de qualidade de dados na ingestão.

 • [ ] Configurar CI/CD com GitHub Actions.

 • [ ] Migrar o Data Lake para AWS S3 real (Free Tier).
