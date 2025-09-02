# Deploy com Dokploy - Firecrawl + Lead Enrichment

Este guia explica como implantar a integração de enriquecimento de leads junto com o Firecrawl usando Dokploy.

## 📋 Pré-requisitos

- Dokploy configurado no seu VPS
- Firecrawl já implantado via Dokploy
- SearXNG configurado e funcionando
- Chaves de API: Firecrawl e Google Gemini

## 🔧 Configuração no Dokploy

### 1. Variáveis de Ambiente

No painel do Dokploy, adicione as seguintes variáveis de ambiente ao seu projeto Firecrawl:

```env
# Lead Enrichment Service
FIRECRAWL_API_KEY=fc-your-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
LEAD_ENRICHMENT_PORT=5000
DEBUG=false
```

### 2. Estrutura de Deploy

O serviço será automaticamente implantado como parte do stack do Firecrawl através do `docker-compose.yaml` principal.

**Serviços disponíveis após o deploy:**
- `firecrawl-api`: Porta 3002 (principal)
- `firecrawl-worker`: Worker de background
- `playwright-service`: Serviço de scraping
- `firecrawl-redis`: Cache Redis
- `lead-enrichment`: **NOVO** - Porta 5000

### 3. Endpoints Disponíveis

Após o deploy, os seguintes endpoints estarão disponíveis:

```
# Firecrawl API (principal)
https://seu-dominio.com/

# Lead Enrichment Service
https://seu-dominio.com:5000/
https://seu-dominio.com:5000/enrich-lead
https://seu-dominio.com:5000/enrich-batch
```

## 🚀 Processo de Deploy Automático

### Quando você fizer push:

1. **Dokploy detecta mudanças** no repositório GitHub
2. **Baixa o código** mais recente
3. **Executa docker-compose build** para todos os serviços
4. **Inicia os containers** incluindo o novo serviço `lead-enrichment`
5. **Configura rede interna** para comunicação entre serviços

### Logs de Deploy

Monitor os logs no Dokploy para verificar se todos os serviços subiram corretamente:

```bash
# Logs do serviço principal
docker logs firecrawl-api-1

# Logs do serviço de enriquecimento
docker logs firecrawl-lead-enrichment-1
```

## 🔗 Configuração no N8N

Com o serviço rodando no Dokploy, configure seu N8N para usar:

**URL do serviço**: `http://seu-vps-ip:5000/enrich-lead`

Ou se estiver usando proxy/domínio:
**URL do serviço**: `https://seu-dominio.com:5000/enrich-lead`

### Exemplo de configuração HTTP Request no N8N:

```json
{
  "method": "POST",
  "url": "http://seu-vps-ip:5000/enrich-lead",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "empresa": "{{ $json.empresa }}",
    "telefone": "{{ $json.telefone }}",
    "email": "{{ $json.email }}",
    "row_number": "{{ $json.row_number }}",
    "is_corporate_email": "{{ $json.is_corporate_email }}",
    "domain": "{{ $json.domain }}"
  }
}
```

## 🔍 Verificação de Funcionamento

### 1. Health Check
```bash
curl http://seu-vps-ip:5000/
```

Resposta esperada:
```json
{
  "status": "ok",
  "service": "Firecrawl + Gemini Lead Enrichment",
  "version": "1.0.0"
}
```

### 2. Teste de Enriquecimento
```bash
curl -X POST http://seu-vps-ip:5000/enrich-lead \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": "MARISTELA MODA PET",
    "telefone": "4833655751",
    "email": "maristelamodapet@hotmail.com"
  }'
```

## 🛠️ Troubleshooting

### Problema: Serviço não inicia
**Verificar:**
1. Variáveis de ambiente configuradas no Dokploy
2. Chaves de API válidas
3. Logs de erro: `docker logs firecrawl-lead-enrichment-1`

### Problema: Erro de rede entre serviços
**Solução:**
- Todos os serviços estão na mesma rede Docker (`backend`)
- Use nomes de serviço para comunicação interna: `http://api:3002`

### Problema: Rate limiting
**Configuração:**
- Gemini API: ~60 req/min
- Adicione delays para lotes grandes
- Use endpoint `/enrich-batch` para múltiplos leads

## 📊 Monitoramento

### Logs importantes:
```bash
# Todos os serviços
docker-compose logs -f

# Apenas lead enrichment
docker-compose logs -f lead-enrichment

# Health check
curl http://localhost:5000/ | jq
```

### Métricas de performance:
- Tempo médio de enriquecimento: 5-15 segundos
- Taxa de sucesso esperada: 70-90%
- Uso de memória: ~200-500MB

## 🔄 Atualizações

Para atualizações futuras:

1. **Faça push** das mudanças para o repositório
2. **Dokploy detectará** automaticamente
3. **Rebuild automático** dos containers afetados
4. **Zero downtime** - outros serviços continuam funcionando

## 🆘 Suporte

Se encontrar problemas:

1. Verifique logs no Dokploy
2. Teste endpoints individualmente
3. Confirme conectividade com SearXNG
4. Valide chaves de API

O serviço está pronto para produção e será implantado automaticamente junto com o Firecrawl! 🎯
