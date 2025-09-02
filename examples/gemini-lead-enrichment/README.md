# Firecrawl + Gemini Lead Enrichment

Uma ferramenta para enriquecimento de leads usando Firecrawl (com SearXNG) e Google Gemini, desenvolvida especificamente para integração com N8N workflows.

## Funcionalidades

✅ **Busca Inteligente**: Utiliza Firecrawl search com SearXNG para encontrar informações da empresa  
✅ **Análise com IA**: Usa Google Gemini 2.5 Pro para analisar e extrair informações relevantes  
✅ **Enriquecimento Completo**: Encontra site oficial, telefones, emails, CNPJ, endereço e redes sociais  
✅ **Score de Confiança**: Avalia a qualidade das informações encontradas  
✅ **Compatível com N8N**: JSON de entrada e saída otimizado para workflows  

## Instalação

1. Clone o repositório e navegue até o diretório:
```bash
cd examples/gemini-lead-enrichment
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

## Configuração

### Chaves de API Necessárias:

1. **FIRECRAWL_API_KEY**: Obtenha em [firecrawl.dev](https://firecrawl.dev)
2. **GEMINI_API_KEY**: Obtenha em [Google AI Studio](https://aistudio.google.com)

### Arquivo .env:
```env
FIRECRAWL_API_KEY=fc-your-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

## Uso

### Linha de Comando
```bash
python lead-enrichment.py
```

### Importação em Python
```python
from lead_enrichment import LeadEnrichmentService

service = LeadEnrichmentService()

# Dados do lead
lead_data = {
    "empresa": "MARISTELA MODA PET",
    "telefone": "4833655751", 
    "email": "maristelamodapet@hotmail.com",
    "row_number": 2,
    "is_corporate_email": "false",
    "domain": ""
}

# Enriquecer lead
result = service.enrich_lead_from_json(lead_data)
print(result)
```

## Integração com N8N

### Passo 1: Configurar o Servidor
```bash
# Instalar dependências
./install.sh

# Iniciar servidor Flask
python3 flask-server.py
```

O servidor estará disponível em `http://localhost:5000`

### Passo 2: Importar Workflow
1. Abra o N8N
2. Importe o arquivo `n8n-workflow.json`
3. Configure as credenciais do Google Sheets
4. Ajuste os IDs das planilhas nos nós

### Passo 3: Configurar Planilha Origem
Sua planilha deve ter as colunas:
- `empresa` - Nome da empresa
- `telefone` - Telefone (opcional)
- `email` - Email (opcional)
- `row_number` - Número da linha
- `is_corporate_email` - "true" ou "false"
- `domain` - Domínio do email (deixe vazio para emails genéricos)

### Passo 4: Configurar Planilha Destino
Crie uma planilha "Leads_Enriquecidos" com as colunas:
- `empresa`
- `telefone_original`
- `email_original`
- `website`
- `telefones_adicionais`
- `emails_adicionais`
- `cnpj`
- `endereco`
- `instagram`
- `facebook`
- `linkedin`
- `confidence_score`
- `data_enriquecimento`

### Fluxo do Workflow N8N:

1. **Google Sheets Trigger**: Monitora novas linhas na planilha
2. **Filtrar Emails Genéricos**: Processa apenas leads com emails não corporativos
3. **Enriquecer Lead**: Chama o serviço de enriquecimento
4. **Verificar Sucesso**: Confirma se o enriquecimento foi bem-sucedido
5. **Processar Dados**: Organiza os dados para inserção
6. **Atualizar Planilha**: Salva os dados enriquecidos
7. **Notificar Telegram**: Envia notificação (opcional)

## Formato de Resposta

```json
{
    "original_data": {
        "empresa": "MARISTELA MODA PET",
        "telefone": "4833655751",
        "email": "maristelamodapet@hotmail.com",
        "row_number": 2,
        "is_corporate_email": "false",
        "domain": ""
    },
    "enriched_data": {
        "website": "https://maristelamodapet.com.br",
        "additional_phones": ["(48) 99136-2131"],
        "additional_emails": ["contato@maristelamodapet.com.br"],
        "cnpj": "00.266.180/0001-58",
        "endereco": "R. Manoel Pizolati, 408 Jardim Atlântico, Florianópolis - SC 88095-360",
        "redes_sociais": {
            "instagram": "https://www.instagram.com/maristelamodapetoficial/",
            "facebook": "https://www.facebook.com/maristelamodapetoficial/"
        },
        "confidence_score": 95,
        "search_results_used": [
            "https://maristelamodapet.com.br/",
            "https://www.instagram.com/maristelamodapetoficial/"
        ]
    }
}
```

## Workflow N8N Sugerido

O workflow inclui os seguintes nós:

1. **Google Sheets Trigger**: Monitora novas linhas na planilha de leads
2. **Function Node**: Filtra apenas leads com emails genéricos (Gmail, Hotmail, etc.)
3. **HTTP Request**: Chama o serviço de enriquecimento
4. **Set Node**: Organiza os dados retornados
5. **Google Sheets Update**: Atualiza a planilha com as novas informações
6. **Telegram Notification**: Notifica sobre leads processados (opcional)

### Configuração Automática
Use o arquivo `n8n-workflow.json` para importar o workflow completo no N8N.

## Troubleshooting

### Erro: "FIRECRAWL_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe e contém sua chave da API
- Execute: `cp .env.example .env` e edite com suas chaves

### Erro: "Import 'flask' could not be resolved"
- Execute: `pip3 install -r requirements.txt`
- Verifique se está usando o Python correto

### Erro: "Connection refused" no N8N
- Verifique se o servidor Flask está rodando: `python3 flask-server.py`
- Confirme se a URL no N8N está correta: `http://localhost:5000/enrich-lead`

### Baixo Score de Confiança
- Empresa pode ter pouca presença online
- Tente buscar com variações do nome da empresa
- Verifique se os resultados de busca são relevantes

### Rate Limiting
- O Gemini tem limites de requisições por minuto
- Adicione delays entre requisições para lotes grandes
- Use o endpoint `/enrich-batch` para processar múltiplos leads

### Sem Resultados de Busca
- Verifique se o SearXNG está funcionando
- Teste com empresas conhecidas primeiro
- Confirme se sua chave do Firecrawl tem créditos

## Deploy em Produção

### Dokploy (VPS)
Se você estiver usando Dokploy para deploy automático:

1. **Configure variáveis de ambiente** no painel do Dokploy:
   ```env
   FIRECRAWL_API_KEY=fc-your-api-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   LEAD_ENRICHMENT_PORT=5000
   ```

2. **Faça push** das mudanças - Dokploy implantará automaticamente
3. **Serviço estará disponível** em `http://seu-vps:5000`

Consulte `DOKPLOY.md` para instruções detalhadas.

### Docker Manual
```bash
# Build da imagem
docker build -t lead-enrichment .

# Executar container
docker run -d \
  -p 5000:5000 \
  -e FIRECRAWL_API_KEY=your-key \
  -e GEMINI_API_KEY=your-key \
  lead-enrichment
```

### Score de Confiança
- **90-100**: Informações muito confiáveis (site oficial + múltiplas fontes)
- **70-89**: Informações confiáveis (boa consistência entre fontes)
- **50-69**: Informações moderadamente confiáveis
- **0-49**: Informações pouco confiáveis

### Tratamento de Erros
A ferramenta inclui tratamento robusto de erros para:
- APIs indisponíveis
- Limites de rate limiting
- Resultados de busca vazios
- Respostas mal formadas do Gemini

## Limitações

- Dependente da qualidade dos resultados de busca
- Sujeito aos limites de rate da API do Gemini
- Nem todas as empresas têm presença web adequada

## Suporte

Para dúvidas ou problemas, consulte:
- [Documentação do Firecrawl](https://docs.firecrawl.dev)
- [Documentação do Gemini](https://ai.google.dev/docs)
- Issues neste repositório

## Licença

Este projeto segue a mesma licença do projeto Firecrawl principal.
