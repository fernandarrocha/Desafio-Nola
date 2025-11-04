# 📊 Estrutura de Dados

## Visão Geral

Esse documento descreve a característica de geração de dados adotada pelo script generate_data.py

Resultado final: Banco PostgreSQL com **6 meses de dados operacionais** de restaurantes, espelhando o sistema real da Arcca que gerencia 1000+ estabelecimentos.

## Schema Principal

### Hierarquia de Vendas

```
Sale (Venda)
├── Store (Loja)
├── Channel (Canal: presencial/delivery)
├── Customer (Cliente - opcional, 70% identificados)
│
├── ProductSales[] (1-5 produtos por venda)
│   ├── Product
│   └── ItemProductSales[] (customizações: "sem cebola", "+bacon")
│       ├── Item (complemento/adicional)
│       ├── OptionGroup (grupo: "Adicionais", "Remover")
│       └── ItemItemProductSales[] (itens em itens - nested)
│
├── Payments[] (1-2 formas de pagamento)
│   └── PaymentType
│
└── DeliverySale (se delivery)
    ├── Courier info (entregador)
    └── DeliveryAddress
```

### Tabelas Core

```sql
-- Vendas (núcleo)
sales (
    id, store_id, channel_id, customer_id, sub_brand_id,
    created_at, customer_name, sale_status_desc,
    total_amount_items, total_discount, total_increase,
    delivery_fee, service_tax_fee, total_amount, value_paid,
    production_seconds, delivery_seconds, people_quantity,
    discount_reason, origin
)

-- Produtos vendidos
product_sales (
    id, sale_id, product_id,
    quantity, base_price, total_price, observations
)

-- Customizações de produtos (ex: "Hamburguer + Bacon + Queijo extra")
item_product_sales (
    id, product_sale_id, item_id, option_group_id,
    quantity, additional_price, price, observations
)

-- Customizações nested (ex: "Bacon + Cheddar cremoso")
item_item_product_sales (
    id, item_product_sale_id, item_id, option_group_id,
    quantity, additional_price, price
)

-- Dados de entrega (apenas pedidos delivery)
delivery_sales (
    id, sale_id,
    courier_name, courier_phone, courier_type,
    delivery_type, status, delivery_fee, courier_fee
)

delivery_addresses (
    id, sale_id, delivery_sale_id,
    street, number, complement, neighborhood,
    city, state, postal_code, latitude, longitude
)

-- Pagamentos (venda pode ter múltiplos)
payments (
    id, sale_id, payment_type_id, value, is_online
)

-- Catálogo
products (id, brand_id, category_id, name)
items (id, brand_id, category_id, name)  -- Complementos
option_groups (id, brand_id, name)  -- Grupos de opções
categories (id, brand_id, name, type)  -- 'P' produto, 'I' item

-- Entidades
stores (id, name, city, state, is_active, is_own)
channels (id, name, type)  -- 'P' presencial, 'D' delivery
customers (id, customer_name, email, phone_number, birth_date)
payment_types (id, description)
```

## Volume de Dados

```
50 lojas → 500.000 vendas → 1.2M produtos vendidos → 800k customizações
         ↓
   10k clientes (70% das vendas identificadas)
```

### Distribuição

**Vendas por canal**:
- Presencial: 40% (~200k vendas)
- iFood: 30% (~150k)
- Rappi: 15% (~75k)
- Outros: 15% (~75k)

**Produtos**:
- 500 produtos base
- 200 items/complementos
- Média 2.4 produtos por venda
- 60% das vendas têm customizações

**Clientes**:
- 10.000 cadastrados
- 30% vendas são "guest" (sem cadastro)
- Distribuição: 70% compraram 1-3x, 20% 4-10x, 10% 10+x

## Padrões Temporais

### Intra-dia
```
00-06h: 2% das vendas
06-11h: 8%
11-15h: 35% ⚡ (almoço)
15-19h: 10%
19-23h: 40% ⚡ (jantar)
23-24h: 5%
```

### Semanal
```
Segunda:  -20% vs média
Terça:    -10%
Quarta:    -5%
Quinta:     0% (baseline)
Sexta:    +30%
Sábado:   +50% ⚡
Domingo:  +40%
```

### Mensal
- Crescimento gradual: ~2-3% mês a mês
- Variação aleatória: ±10%

## Dados Realistas

### Valores Típicos

```
Ticket médio geral: R$ 65
├── Presencial: R$ 45-55
├── iFood: R$ 70-85
└── Rappi: R$ 65-80

Tempos operacionais:
├── Preparo: 5-40 min (média 18 min)
└── Entrega: 15-60 min (média 35 min)

Taxas:
├── Cancelamento: ~5%
├── Com desconto: ~20%
└── Com customização: ~60%
```

### Anomalias Injetadas

Propositalmente incluímos para testar analytics:

1. **Semana problemática**: Queda de 30% em vendas (simula problema operacional)
2. **Dia promocional**: Pico de 3x (Black Friday, promoção)
3. **Loja crescendo**: Uma loja específica com crescimento linear de 5%/mês
4. **Produto sazonal**: Alguns produtos vendem 80% mais em determinados meses

**Sua solução deve permitir identificar esses padrões.**

## Complexidade dos Dados

### Exemplo Real de Venda

```
Venda #12345
├── Loja: "Burguer House - Centro SP"
├── Canal: iFood
├── Cliente: João Silva (identificado)
├── Total: R$ 87,50
│
├── Produtos:
│   ├── X-Bacon Duplo (R$ 32,00)
│   │   ├── + Bacon extra (R$ 5,00)
│   │   ├── + Cheddar cremoso (R$ 4,00)
│   │   └── - Cebola (R$ 0,00)
│   │
│   ├── Batata Frita Grande (R$ 18,00)
│   │   └── + Cheddar (R$ 3,00)
│   │
│   └── Refrigerante 2L (R$ 12,00)
│
├── Desconto: -R$ 8,50 (cupom fidelidade)
├── Taxa entrega: +R$ 9,00
├── Total: R$ 87,50
│
├── Pagamento: PIX (R$ 87,50)
│
├── Tempos:
│   ├── Preparo: 22 minutos
│   └── Entrega: 38 minutos
│
└── Entrega:
    ├── Entregador: Carlos (iFood)
    └── Endereço: Rua X, 123, Centro
```

Esta estrutura permite análises como:
- "Qual item adicional mais vendido?"
- "Produtos que mais recebem remoções?"
- "Tempo de entrega por região?"
- "Mix de pagamentos por canal?"

## Queries de Exemplo

```sql
-- Vendas completas com produtos e customizações
SELECT 
    s.id, s.created_at, s.total_amount,
    st.name as store, ch.name as channel,
    p.name as product,
    ps.quantity,
    array_agg(i.name) as customizations
FROM sales s
JOIN stores st ON st.id = s.store_id
JOIN channels ch ON ch.id = s.channel_id
JOIN product_sales ps ON ps.sale_id = s.id
JOIN products p ON p.id = ps.product_id
LEFT JOIN item_product_sales ips ON ips.product_sale_id = ps.id
LEFT JOIN items i ON i.id = ips.item_id
WHERE s.sale_status_desc = 'COMPLETED'
  AND DATE(s.created_at) = '2024-01-15'
GROUP BY s.id, st.name, ch.name, p.name, ps.quantity
LIMIT 10;

-- Top itens/complementos mais vendidos
SELECT 
    i.name as item,
    COUNT(*) as times_added,
    SUM(ips.additional_price) as revenue_generated
FROM item_product_sales ips
JOIN items i ON i.id = ips.item_id
JOIN product_sales ps ON ps.id = ips.product_sale_id
JOIN sales s ON s.id = ps.sale_id
WHERE s.sale_status_desc = 'COMPLETED'
GROUP BY i.name
ORDER BY times_added DESC
LIMIT 20;

-- Performance de entrega por região
SELECT 
    da.neighborhood,
    da.city,
    COUNT(*) as deliveries,
    AVG(s.delivery_seconds / 60.0) as avg_delivery_minutes,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY s.delivery_seconds / 60.0) as p90_delivery_minutes
FROM sales s
JOIN delivery_addresses da ON da.sale_id = s.id
WHERE s.sale_status_desc = 'COMPLETED'
  AND s.delivery_seconds IS NOT NULL
GROUP BY da.neighborhood, da.city
HAVING COUNT(*) >= 10
ORDER BY avg_delivery_minutes DESC;
```

## Script de Geração

Execute para popular o banco:

```bash
python generate_data.py \
    --months 6 \
    --stores 50 \
    --products 500 \
    --items 200 \
    --customers 10000
```

Isso gera:
- ~500k vendas
- ~1.2M produtos vendidos
- ~800k customizações (items)
- ~200k entregas com endereço
- ~600k pagamentos

**Tempo estimado**: 5-15 minutos dependendo da máquina.

## O Que Isso Habilita

Com essa estrutura completa, sua solução pode responder:

- Faturamento total, ticket médio, vendas por dia
- Rankings de lojas e produtos
- Performance por canal e horário
- Taxa de cancelamento e motivos
- Análise de descontos
- **Customizações**: Quais items mais vendidos? Quais produtos recebem mais alterações?
- **Delivery**: Tempo médio por região? Quais bairros mais pedem?
- **Mix de produtos**: Quais combinações aparecem juntas?
- **Jornada do cliente**: Frequência, retenção, lifetime value
- Detecção de anomalias temporais
- Previsão de demanda por produto
- Segmentação de clientes
- Otimização de rotas de entrega

---

**A complexidade dos dados reflete operações reais. Use isso a seu favor para criar analytics ricos.**
