# 📊 NOLA God Level Coder - Analytics para Restaurantes

Esta é a minha solução para o desafio [NOLA God Level Coder](https://github.com/lucasvieira94/nola-god-level). O objetivo é uma plataforma de analytics customizável para que donos de restaurantes, possam explorar seus dados operacionais de forma simples, flexível e rápida.

**Autora:** Fernanda Rcoha da Silva
**Prazo de Entrega:** 03/11/2025

---

## 🚀 Demonstração (Deploy)

[!! SE VOCÊ FEZ O DEPLOY NO STREAMLIT CLOUD, INSIRA O LINK AQUI. SENÃO, APAGUE ESTA SEÇÃO E FOQUE NAS INSTRUÇÕES DO DOCKER ABAIXO !!]

---

## 🏛️ A Decisão Arquitetural: Por que ETL + Parquet?

O ponto central da minha arquitetura foi uma decisão consciente para resolver o principal desafio técnico: **Performance**.

### O Problema

O requisito de avaliação era claro: "Queries otimizadas (menos de 1 segundo para 500k registros)". O schema de dados fornecido, apesar de realista, é transacional (OLTP), exigindo múltiplos e complexos `JOINs` para responder perguntas simples (ex: `sales` -> `product_sales` -> `products` -> `categories` -> `stores` -> `channels`).

Uma abordagem ingênua, conectando o dashboard diretamente ao PostgreSQL e executando esses `JOINs` a cada clique de filtro, falharia miseravelmente no requisito de < 1s.

### A Solução (Arquitetura OLAP)

Para garantir uma experiência de usuário "fluida" e performance instantânea, optei por uma arquitetura analítica (OLAP) desacoplada em duas etapas:

1.  **ETL (Extract, Transform, Load):** Um script Python (`etl.py`) é executado uma vez. Ele se conecta ao PostgreSQL, executa a query complexa com todos os `JOINs` *uma única vez*, e transforma os dados em uma tabela "achatada" (denormalizada).
2.  **Data Mart (Parquet):** Este script salva o resultado em um arquivo `dados_analiticos.parquet`. O formato Parquet é colunar, otimizado para compressão e leitura analítica de alta velocidade.
3.  **Dashboard (Streamlit):** O aplicativo `app.py` (o dashboard) **nunca toca no banco de dados**. Ele lê *apenas* o arquivo Parquet na memória (usando `@st.cache_data`).

**Resultado:** A filtragem é feita em *milissegundos* pelo Pandas, pois os dados já estão na memória, pré-processados. Isso não só atende, mas supera o requisito de performance.

---

## ✨ Funcionalidades Implementadas

O dashboard foi projetado para resolver as "Dores Atuais" do cliente:

* **Painel de KPIs Dinâmicos:** Cards no topo da página mostram Faturamento Total, Nº de Pedidos, Ticket Médio e Tempo Médio de Entrega, todos reagindo aos filtros em tempo real.
* **Gráfico de Performance por Hora:** Um gráfico de linha interativo que permite à Maria visualizar os picos de venda ao longo do dia (ex: almoço vs. jantar).
* **Insights Automáticos (IA Baseada em Regras):** Um botão "Gerar Insights" que analisa os dados filtrados e aponta:
    * **Dia de Pico (Black Friday):** Detecta anomalias de faturamento (como o "Pico de 3x" injetado nos dados).
    * **Horário de Pico:** Informa qual a hora mais lucrativa.
    * **Canal Mais Usado:** Mostra qual canal (iFood, Rappi, etc.) teve mais pedidos.
* **Construtor de Análise (Pivot Table):** O coração do dashboard. Permite que o usuário cruze qualquer Métrica (ex: "Valor Total") com qualquer Dimensão (ex: "Produto" por "Canal"), criando relatórios flexíveis.
* **Filtros Globais:** Filtros na barra lateral por Data, Loja e Canal.
* **Exportação para CSV:** Qualquer análise da tabela dinâmica pode ser exportada com um clique, atendendo ao critério de "Exportar relatório".
* **UI Customizada:** O dashboard usa um tema customizado (`.streamlit/config.toml`) para uma aparência profissional.

---

## 🛠️ Stack Tecnológica

* **Infraestrutura:** Docker, Docker Compose
* **Banco de Dados:** PostgreSQL (para geração de dados)
* **ETL (Backend):** Python, Pandas, SQLAlchemy (para conectar ao PG), PyArrow (para salvar Parquet)
* **Dashboard (Frontend):** Streamlit, Plotly Express (para gráficos interativos), Pillow (para imagens)

---

## 🏃 Como Rodar (Entrega Docker)

Este projeto está 100% "dockerizado" para garantir que ele funcione perfeitamente, como solicitado no `FAQ.md` ("garanta que `docker compose up` funciona perfeitamente").

**Pré-requisitos:**
* Docker Desktop (Instalado e em execução)

### Instruções

1.  Clone este repositório:
    ```bash
    git clone [!! INSIRA O LINK DO SEU REPOSITÓRIO GIT AQUI !!]
    ```

2.  Entre na pasta do projeto:
    ```bash
    cd nola-god-level
    ```

3.  Execute o Docker Compose para construir e iniciar todos os serviços (Banco, ETL e App):
    ```bash
    docker compose up --build
    ```

4.  **Aguarde!** O primeiro `up` irá:
    * Construir a imagem do `postgres` e iniciá-lo.
    * Construir a imagem do `app` (instalando o Streamlit, Pandas, etc.).
    * Assim que o banco estiver pronto, o container `app` irá rodar o `etl.py`. (Isso pode levar de 1 a 3 minutos, você verá o log "Iniciando script de ETL..." no seu terminal).
    * Assim que o ETL terminar, o servidor Streamlit iniciará.

5.  Acesse o dashboard no seu navegador:
    **[http://localhost:8501](http://localhost:8501)**
