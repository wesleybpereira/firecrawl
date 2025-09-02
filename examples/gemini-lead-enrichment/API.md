# API Documentation - Firecrawl + Gemini Lead Enrichment

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Health Check
**GET** `/`

Verifica se o serviço está funcionando.

**Response:**
```json
{
    "status": "ok",
    "service": "Firecrawl + Gemini Lead Enrichment",
    "version": "1.0.0"
}
```

### 2. Enrich Single Lead
**POST** `/enrich-lead`

Enriquece um lead único com informações adicionais.

**Request Body:**
```json
{
    "empresa": "MARISTELA MODA PET",           // Obrigatório
    "telefone": "4833655751",                 // Opcional
    "email": "maristelamodapet@hotmail.com",  // Opcional
    "row_number": 2,                          // Opcional
    "is_corporate_email": "false",            // Opcional
    "domain": ""                              // Opcional
}
```

**Response (Success):**
```json
{
    "success": true,
    "data": {
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
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Não foi possível enriquecer o lead",
    "data": null
}
```

### 3. Enrich Batch
**POST** `/enrich-batch`

Enriquece múltiplos leads em uma única requisição.

**Request Body:**
```json
{
    "leads": [
        {
            "empresa": "MARISTELA MODA PET",
            "telefone": "4833655751",
            "email": "maristelamodapet@hotmail.com",
            "row_number": 2,
            "is_corporate_email": "false",
            "domain": ""
        },
        {
            "empresa": "Outra Empresa",
            "telefone": "48999999999",
            "email": "teste@gmail.com",
            "row_number": 3,
            "is_corporate_email": "false",
            "domain": ""
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "batch_stats": {
        "total": 2,
        "successful": 1,
        "failed": 1
    },
    "results": [
        {
            "index": 0,
            "success": true,
            "error": null,
            "data": {
                // ... dados enriquecidos ...
            }
        },
        {
            "index": 1,
            "success": false,
            "error": "Não foi possível enriquecer o lead",
            "data": null
        }
    ]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request - Dados inválidos ou campos obrigatórios ausentes |
| 404  | Not Found - Lead não pôde ser enriquecido |
| 500  | Internal Server Error - Erro interno do servidor |

## Fields Description

### Input Fields
- **empresa** (string, required): Nome da empresa a ser pesquisada
- **telefone** (string, optional): Telefone original do lead
- **email** (string, optional): Email original do lead
- **row_number** (number, optional): Número da linha na planilha
- **is_corporate_email** (string, optional): "true" ou "false"
- **domain** (string, optional): Domínio do email

### Output Fields
- **website** (string): Site oficial da empresa encontrado
- **additional_phones** (array): Lista de telefones adicionais encontrados
- **additional_emails** (array): Lista de emails corporativos encontrados
- **cnpj** (string): CNPJ da empresa, se encontrado
- **endereco** (string): Endereço completo da empresa
- **redes_sociais** (object): URLs das redes sociais (instagram, facebook, linkedin)
- **confidence_score** (number): Score de confiança de 0-100
- **search_results_used** (array): URLs utilizadas para extração dos dados

## Confidence Score

| Range | Description |
|-------|-------------|
| 90-100| Informações muito confiáveis (site oficial + múltiplas fontes) |
| 70-89 | Informações confiáveis (boa consistência entre fontes) |
| 50-69 | Informações moderadamente confiáveis |
| 0-49  | Informações pouco confiáveis |

## Rate Limits

- **Gemini API**: ~60 requests/minute (varia por tier)
- **Firecrawl API**: Conforme seu plano
- **Recomendação**: Para lotes grandes, use delays entre requisições

## Examples

### cURL Example
```bash
curl -X POST http://localhost:5000/enrich-lead \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": "MARISTELA MODA PET",
    "telefone": "4833655751",
    "email": "maristelamodapet@hotmail.com"
  }'
```

### Python Example
```python
import requests

data = {
    "empresa": "MARISTELA MODA PET",
    "telefone": "4833655751",
    "email": "maristelamodapet@hotmail.com"
}

response = requests.post(
    "http://localhost:5000/enrich-lead",
    json=data
)

result = response.json()
print(result)
```

### JavaScript Example
```javascript
const data = {
    empresa: "MARISTELA MODA PET",
    telefone: "4833655751",
    email: "maristelamodapet@hotmail.com"
};

fetch('http://localhost:5000/enrich-lead', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => console.log(result));
```
