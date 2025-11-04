# ⚡ Quick Start - 5 Minutos

ATENÇÃO: essa é uma sugestão de setup, não é obrigatório que se rode dessa maneira. O script base para geração de dados está em ./generate_data.py.

## Setup Completo

```bash
# 1. Clone
git clone https://github.com/lucasvieira94/nola-god-level.git
cd nola-god-level


docker compose down -v 2>/dev/null || true
docker compose build --no-cache data-generator
docker compose up -d postgres
docker compose run --rm data-generator
docker compose --profile tools up -d pgadmin
```

**Aguarde 5-15 minutos** enquanto 500k vendas são geradas.

## Verifique

```bash
docker compose exec postgres psql -U challenge challenge_db -c 'SELECT COUNT(*) FROM sales;'

# Deve mostrar ~500k
```

## Explore

Explore os dados gerados da forma como quiser e julgar mais eficiente. Navegue pelas tableas e entenda seus relacionamentos.

## Estrutura dos Dados

```
Sale
├── ProductSale (produtos)
│   └── ItemProductSale (customizações: +bacon, -cebola)
├── Payment (formas de pagamento)
└── DeliverySale (delivery)
    └── DeliveryAddress (com lat/long)
```

**Schema completo**: [DADOS.md](./DADOS.md)

## Próximos Passos

1. **Entenda o problema**: Leia [PROBLEMA.md](./PROBLEMA.md)
2. **Explore os dados**: Rode queries, veja padrões
3. **Desenhe solução**: Arquitetura, stack, UX
4. **Implemente**: Resolva o problema!

---

**Setup completo! Hora de codar. 🚀**
