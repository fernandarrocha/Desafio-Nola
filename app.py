import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
# Usar "wide" para que o dashboard ocupe toda a largura
st.set_page_config(page_title="NOLA God Level - Analytics para Restaurantes", page_icon="📊", layout="wide")
st.title("NOLA Insights")
st.markdown("Bem-vindo ao NOLA Insights! Use os filtros na barra lateral para explorar os dados de vendas do seu restaurante e gerar insights valiosos.")

# --- Carregamento dos Dados ---

@st.cache_data
def load_data():

    try:
        df = pd.read_parquet("dados_analiticos.parquet")
        df['data_venda'] = pd.to_datetime(df['data_venda'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame() 
df = load_data()

# Mapeia os dias da semana, para nomes em Português
dias_semana_map = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}

# Cria a nova coluna no DataFrame principal
df['dia_semana'] = df['data_venda'].dt.dayofweek.map(dias_semana_map)


if df.empty:
    st.stop() # Para a execução se os dados não puderam ser carregados

# --- Sidebar  ---
st.sidebar.title("Filtros")


# Filtro de Data
min_data = df['data_venda'].min().date()
max_data = df['data_venda'].max().date()

data_inicio = st.sidebar.date_input("Data Início", min_data, min_value=min_data, max_value=max_data, format="DD/MM/YYYY")
data_fim = st.sidebar.date_input("Data Fim", max_data, min_value=min_data, max_value=max_data, format="DD/MM/YYYY")


# Garantir que a data fim seja maior ou igual a data início
if data_inicio > data_fim:
    st.sidebar.error("Data de início não pode ser maior que a data de fim.")
    st.stop()

# Filtro de Lojas 
lojas_disponiveis = df['loja_nome'].unique()
lojas_selecionadas = st.sidebar.multiselect("Lojas", lojas_disponiveis, default=lojas_disponiveis)

# Filtro de Canais 
canais_disponiveis = df['canal_nome'].unique()
canais_selecionados = st.sidebar.multiselect("Canais", canais_disponiveis, default=canais_disponiveis)

# Filtro de Dia da Semana
dias_disponiveis = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
dias_selecionados = st.sidebar.multiselect("Dia da Semana", dias_disponiveis, default=dias_disponiveis)

# --- Aplicação dos Filtros ---
# Filtra o DataFrame principal com base nas seleções
df_filtrado = df[
    (df['data_venda'].dt.date >= data_inicio) &
    (df['data_venda'].dt.date <= data_fim) &
    (df['loja_nome'].isin(lojas_selecionadas)) &
    (df['canal_nome'].isin(canais_selecionados)) &
    (df['dia_semana'].isin(dias_selecionados))
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

## --- BLOCO DE KPIs ---

try:
    # Calcular os KPIs (usando o df_filtrado)
    total_revenue = df_filtrado['produto_valor_total'].sum()
    total_orders = df_filtrado['venda_id'].nunique()
    
    # Evitar divisão por zero
    if total_orders > 0:
        avg_ticket = total_revenue / total_orders
    else:
        avg_ticket = 0

    # KPI Bônus: Tempo Médio de Entrega
    df_delivery = df_filtrado[df_filtrado['tempo_entrega_seg'] > 0] # Filtra só pedidos com entrega
    if not df_delivery.empty:
        avg_delivery_time = df_delivery['tempo_entrega_seg'].mean() / 60 # Converte para minutos
    else:
        avg_delivery_time = 0

    # Exibição dos KPIs em colunas
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="large") # 'gap="large"' dá um bom espaço

    with kpi1:
        st.info("Faturamento Total", icon="💰")
        st.metric(
            label="Faturamento Total (R$)", # O label é importante para o Streamlit
            value=f"R$ {total_revenue:,.2f}",
            label_visibility="collapsed" # Esconde o label, já que st.info é o título
        )

    with kpi2:
        st.info("Total de Pedidos", icon="🛒")
        st.metric(
            label="Total de Pedidos",
            value=f"{total_orders:,}",
            label_visibility="collapsed"
        )

    with kpi3:
        st.info("Ticket Médio", icon="💵")
        st.metric(
            label="Ticket Médio (R$)",
            value=f"R$ {avg_ticket:,.2f}",
            label_visibility="collapsed"
        )
    
    with kpi4:
        st.info("Tempo Médio Entrega", icon="⏱️")
        st.metric(
            label="Tempo Médio Entrega (min)",
            value=f"{avg_delivery_time:,.0f} min",
            label_visibility="collapsed"
        )

except Exception as e:
    st.error(f"Erro ao calcular KPIs: {e}")
# --- FIM DO NOVO BLOCO DE KPIs ---

# --- BLOCO DE INSIGHTS ---
st.markdown("---") # Adiciona uma linha divisória
st.markdown("### Insights Automáticos")

if st.button("Gerar Insights sobre o período filtrado"):
    try:
        # Verifica se o dataframe filtrado não está vazio
        if df_filtrado.empty:
            st.warning("Não há dados no período selecionado para gerar insights.")
        else:
            
            # --- Insight de Dia de Pico ---
            # Agrupa dados por dia (resample é bom para time series)
            df_dia = df_filtrado.set_index('data_venda')['produto_valor_total'].resample('D').sum()
            
            dia_pico = df_dia.idxmax()
            valor_pico = df_dia.max()
            media_vendas_dia = df_dia.mean()

            # Lógica para detectar a anomalia "Pico de 3x"
            if valor_pico > (media_vendas_dia * 2.5) and media_vendas_dia > 0: # 2.5x já é um bom indicador
                st.info(f"💡 **Pico (Promoção):** O dia **{dia_pico.strftime('%d/%m/%Y')}** teve um faturamento de {valor_pico:,.2f}, que é muito acima da média diária que é (R$ {media_vendas_dia:,.2f}). Isso indica um evento especial, como a **Black Friday** ou uma grande promoção!")
            else:
                st.info(f"💡 **Pico (Dia):** O dia de maior faturamento foi **{dia_pico.strftime('%d/%m/%Y')}** com **R$ {valor_pico:,.2f}**.")
            
            # --- Insight de Horário de Pico ---
            # Reutiliza a lógica do gráfico de horas
            df_hora_insight = df_filtrado.copy()
            df_hora_insight['hora_dia'] = df_hora_insight['data_venda'].dt.hour
            df_analise_hora_insight = df_hora_insight.groupby('hora_dia')['produto_valor_total'].sum()
            
            hora_pico = df_analise_hora_insight.idxmax()
            st.success(f"🚀 **Horário:** O horário de pico de vendas (maior faturamento) no período é às **{hora_pico}h**.")

            # --- Insight de Produto (Bônus) ---
            produto_top = df_filtrado.groupby('produto_nome')['produto_valor_total'].sum().idxmax()
            st.success(f"🚀 **Produto:** O produto de maior faturamento no período foi **{produto_top}**.")

            # --- Insight de Canal Mais Usado ---
           
            canal_top_pedidos = df_filtrado.groupby('canal_nome')['venda_id'].nunique().idxmax()
            faturamento_canal_top = df_filtrado[df_filtrado['canal_nome'] == canal_top_pedidos]['produto_valor_total'].sum()

            st.success(f"🏆 **Canal:** O canal com **mais pedidos** no período foi o **{canal_top_pedidos}**, gerando **R$ {faturamento_canal_top:,.2f}**.")
    
    except Exception as e:
        st.error(f"Erro ao gerar insights: {e}")
        st.warning("Dica: Certifique-se de que há dados no período selecionado.")
        
st.markdown("---") 


# --- GRÁFICO DE ANÁLISE POR HORA ---
st.subheader("Visão Geral: Performance por Hora do Dia")
st.markdown("Use os filtros da barra lateral para ver a performance ao longo do dia.")

try:
    # Preparar os dados para este gráfico
    df_hora = df_filtrado.copy()
    df_hora['hora_dia'] = df_hora['data_venda'].dt.hour
    
    # Agrupar por hora e calcular o total de vendas 
    df_analise_hora = df_hora.groupby('hora_dia')['produto_valor_total'].sum().reset_index()
    
    # Renomear colunas para o gráfico
    df_analise_hora.rename(columns={
        'hora_dia': 'Hora do Dia',
        'produto_valor_total': 'Valor Total (R$)'
    }, inplace=True)

    # Gráfico de Linha 
    fig_hora = px.line(
        df_analise_hora,
        x='Hora do Dia',
        y='Valor Total (R$)',
        title="Performance de Vendas por Hora",
        markers=True  
    )
    
    # Força o eixo X a mostrar todas as 24h
    fig_hora.update_layout(xaxis=dict(tickmode='linear', dtick=1))
    
    # Exibir o gráfico
    st.plotly_chart(fig_hora, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao gerar o gráfico de performance por hora: {e}")

st.markdown("---") 

st.markdown("Use os seletores abaixo para criar sua análise, como em uma Tabela Dinâmica.")

# Métricas para analisar
col1, col2, col3 = st.columns(3)

with col1:
    metrica = st.selectbox(
        "Qual métrica você quer analisar?",
        ["Valor Total (R$)", "Nº de Pedidos", "Ticket Médio (R$)", "Tempo de Entrega (min)"]
    )

with col2:
    dimensao_linha = st.selectbox(
        "Agrupar linhas por (Dimensão 1):",
        ["Produto", "Categoria", "Loja", "Canal", "Bairro", "Dia da Semana"]
    )

with col3:
    dimensao_coluna = st.selectbox(
        "Agrupar colunas por (Dimensão 2):",  # <-- Argumento 1 (label)
        ["Nenhum", "Canal", "Loja", "Dia da Semana"] # <-- Argumento 2 (options)
    )


# --- Cálculo da Tabela Dinâmica ---

mapa_metricas = {
    "Valor Total (R$)": "produto_valor_total",
    "Nº de Pedidos": "venda_id",
    "Ticket Médio (R$)": "valor_total_venda", # Calcular a média 
    "Tempo de Entrega (min)": "tempo_entrega_seg"
}

mapa_dimensoes = {
    "Produto": "produto_nome",
    "Categoria": "produto_categoria",
    "Loja": "loja_nome",
    "Canal": "canal_nome",
    "Bairro": "bairro_entrega",
    "Dia da Semana": df_filtrado['data_venda'].dt.day_name()
}

# Define a função de agregação
if metrica == "Nº de Pedidos":
    agg_func = pd.Series.nunique # Contagem distinta de vendas
    valor_a_agregar = mapa_metricas[metrica]
elif metrica == "Ticket Médio (R$)":
    agg_func = 'mean'
    valor_a_agregar = mapa_metricas[metrica]
elif metrica == "Tempo de Entrega (min)":
    agg_func = 'mean'
    valor_a_agregar = mapa_metricas[metrica]
    # Converte segundos para minutos
    df_filtrado[valor_a_agregar] = df_filtrado[valor_a_agregar] / 60
else: 
    agg_func = 'sum'
    valor_a_agregar = mapa_metricas[metrica]

try:
    # Cria a tabela dinâmica 
    pivot_table = pd.pivot_table(
        df_filtrado,
        values=valor_a_agregar,
        index=mapa_dimensoes[dimensao_linha],
        columns=mapa_dimensoes[dimensao_coluna] if dimensao_coluna != "Nenhum" else None,
        aggfunc=agg_func,
        fill_value=0 
    )

    # Arredonda os valores
    pivot_table = pivot_table.round(2)

    # --- Exibição dos Resultados ---
    st.subheader(f"{metrica} por {dimensao_linha}" + (f" e {dimensao_coluna}" if dimensao_coluna != "Nenhum" else ""))
    
    # Gráfico Plotly da Tabela Dinâmica
    try:
        # Prepara os eixos X, Y e Cor para o gráfico
        x_axis = mapa_dimensoes[dimensao_linha]
        y_axis = valor_a_agregar

        # 'Dia da Semana' é uma coluna calculada, precisamos garantir que ela exista
        if dimensao_linha == "Dia da Semana":
            df_filtrado['Dia da Semana'] = df_filtrado['data_venda'].dt.day_name()
            x_axis = "Dia da Semana"

        color_axis = None
        if dimensao_coluna != "Nenhum":
            if dimensao_coluna == "Dia da Semana":
                df_filtrado['Dia da Semana'] = df_filtrado['data_venda'].dt.day_name()
                color_axis = "Dia da Semana"
            else:
                color_axis = mapa_dimensoes[dimensao_coluna]

        # Define a função de agregação para o Plotly
        if metrica == "Nº de Pedidos":
            hist_func = 'count' 
        elif metrica == "Ticket Médio (R$)":
            hist_func = 'avg' 
        elif metrica == "Tempo de Entrega (min)":
            hist_func = 'avg'
        else: # Valor Total
            hist_func = 'sum'

        
        fig = px.histogram(
            df_filtrado, 
            x=x_axis,
            y=y_axis,
            color=color_axis, 
            barmode='group',  
            title=f"Análise de {metrica}",
            histfunc=hist_func 
        )

        # Atualiza os eixos para ficarem mais legíveis
        fig.update_layout(xaxis_title=dimensao_linha, yaxis_title=metrica)

        # Exibe o gráfico Plotly no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
       st.error(f"Erro ao gerar o gráfico Plotly: {e}")


    # Mostra a tabela de dados
    st.dataframe(pivot_table, use_container_width=True)
    

    # Mostra um gráfico de barras 
   
    # Botão para exportar o relatório em CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv().encode('utf-8')

    st.download_button(
        label="📥 Exportar Relatório para CSV",
        data=convert_df_to_csv(pivot_table),
        file_name=f"relatorio_{metrica}_{dimensao_linha}.csv",
        mime='text/csv',
    )

except Exception as e:
    st.error(f"Erro ao tentar criar a análise: {e}")
    st.error("Dica: 'Bairro' só funciona bem se o filtro de Canal for 'Delivery'.")

#Tema da página
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            Header {visibility: hidden;}
            </style>
            """
