# Configuração Self-Hosted - Firecrawl + Lead Enrichment

## Para Firecrawl Self-Hosted (Sem Autenticação)

Como você está usando `USE_DB_AUTHENTICATION=false`, não precisa de API key para o Firecrawl.

### Configuração Recomendada no Dokploy

Adicione apenas estas variáveis de ambiente no painel do Dokploy:

```env
# Gemini API Key (obrigatório)
GEMINI_API_KEY=your-gemini-api-key-here

# URL interna do Firecrawl (padrão)
FIRECRAWL_INTERNAL_URL=http://api:3002

# Porta do serviço (opcional)
LEAD_ENRICHMENT_PORT=5000
```

### Como Obter a Gemini API Key

1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Faça login com sua conta Google
3. Clique em "Get API Key"
4. Crie uma nova API key
5. Copie e use no Dokploy

### Opção Alternativa: Com API Key Local

Se quiser usar autenticação local, adicione no seu `.env`:

```env
# No .env principal do Firecrawl
TEST_API_KEY=fc-local-test-key-123456

# No Dokploy
FIRECRAWL_API_KEY=fc-local-test-key-123456
```

### Verificação de Funcionamento

Após o deploy, teste:

```bash
# Health check
curl http://seu-vps:5000/

# Teste de conectividade com Firecrawl interno
curl http://seu-vps:5000/enrich-lead \
  -H "Content-Type: application/json" \
  -d '{"empresa": "Teste Company"}'
```

### Configuração no N8N

Use a URL interna para N8N (se estiver no mesmo VPS):

```
URL: http://lead-enrichment:5000/enrich-lead
```

Ou a URL externa:

```
URL: http://seu-vps-ip:5000/enrich-lead
```

### Troubleshooting

**Erro: "FIRECRAWL_API_KEY não encontrada"**
- Configure `FIRECRAWL_INTERNAL_URL=http://api:3002` no Dokploy
- Ou adicione `FIRECRAWL_API_KEY=fc-local-test-key-123456`

**Erro: Connection refused**
- Verifique se o serviço `api` está rodando
- Confirme que estão na mesma rede Docker

**Erro: Gemini API**
- Verifique se a API key está correta
- Confirme se tem créditos/cota disponível

### Logs para Debug

```bash
# Ver logs do lead enrichment
docker-compose logs -f lead-enrichment

# Ver logs do Firecrawl API
docker-compose logs -f api
```
