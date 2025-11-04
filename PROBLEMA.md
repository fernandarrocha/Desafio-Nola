# 🍔 O Problema: Analytics para Restaurantes

## Contexto

Você foi contratado como tech lead para resolver um problema crítico que afeta 10.000+ restaurantes no Brasil.

## A Persona

**Maria**, dona de 3 restaurantes em São Paulo:
- Vende através de 5 canais (balcão, iFood, Rappi, WhatsApp, app próprio)
- Tem 200+ produtos no cardápio
- Faz ~1.500 pedidos/semana
- Precisa tomar decisões diárias sobre estoque, preços, promoções

### Dores Atuais

**Hoje, Maria não consegue responder**:
- "Qual produto vende mais na quinta à noite no iFood?"
- "Meu ticket médio está caindo. É por canal ou por loja?"
- "Quais produtos têm menor margem e devo repensar o preço?"
- "Meu tempo de entrega piorou. Em quais dias/horários?"
- "Quais clientes compraram 3+ vezes mas não voltam há 30 dias?"

**Ela tem os dados, mas não consegue explorá-los.**

Dashboards fixos mostram apenas visões pré-definidas. Power BI é complexo demais e genérico. Ela não tem time de dados.

## O Desafio Real

Donos de restaurantes precisam de **analytics customizável e flexível**:
- Simples o suficiente para usar sem treinamento técnico
- Poderoso o suficiente para responder perguntas complexas
- Específico ao domínio (métricas de restaurante, não genéricas)

## Dados Disponíveis

Maria tem acesso a:

### Vendas (núcleo)
- Valor total, itens, descontos, taxas
- Horário, data, canal, loja
- Status (completa, cancelada)
- Tempos (preparo, entrega)

### Produtos
- Nome, categoria, preço
- Vendidos em cada pedido
- Com opções/complementos

### Clientes
- Nome, contato, histórico
- Frequência de compra
- Ticket médio

### Operacional
- Canais e suas comissões
- Performance por loja
- Métodos de pagamento

## O que "Boa Solução" Significa

Uma boa solução permite Maria:

1. **Explorar dados livremente**
   - Sem depender de desenvolvedores
   - Criando visualizações customizadas
   - Filtrando por qualquer dimensão

2. **Obter insights acionáveis**
   - Não apenas números, mas significado
   - Comparações temporais
   - Identificação de anomalias

3. **Compartilhar com o time**
   - Gerente de loja vê sua performance
   - Time de marketing vê produtos populares
   - Sócio vê overview financeiro

## Restrições Técnicas

Você **deve usar** o banco de dados PostgreSQL fornecido (500k vendas).

Tudo além disso é **sua decisão arquitetural**:
- Stack tecnológico
- Arquitetura (monolito, microserviços, serverless)
- Frontend framework
- Estratégia de cache
- Deployment

## Não-Requisitos

Você **não precisa**:
- Construir sistema de autenticação completo (mock básico serve)
- Integrar com sistemas externos
- Suportar multi-tenancy
- Escalar para milhões de usuários

Foque em resolver o problema core: **analytics customizável e flexível**.

## Perguntas para Guiar Seu Design

1. Como um usuário não-técnico criaria um dashboard?
2. Como garantir queries rápidas mesmo com milhões de registros?
3. Qual o trade-off entre flexibilidade e simplicidade?
4. Como tornar insights visíveis, não apenas dados?
5. O que diferencia analytics de restaurante de analytics genérico?

## Inspirações

Não copie, mas inspire-se:
- **Metabase**: Simplicidade de query builder
- **Looker**: Modelagem de negócio
- **Amplitude**: UX de analytics
- **Grafana**: Flexibilidade de visualizações
- **Sheets/Excel (Pivot Tables)**: Flexibilidade/adaptabilidade de visualizações

## Critérios de Sucesso

Maria deveria conseguir, em **< 5 minutos**:
1. Ver overview do faturamento do mês
2. Identificar os 10 produtos mais vendidos no delivery
3. Comparar performance de duas lojas
4. Exportar relatório para apresentar ao sócio

Se sua solução permite isso de forma intuitiva, você está no caminho certo.

---

**Este é um problema real que afeta milhares de restaurantes. Como você o resolveria?**

