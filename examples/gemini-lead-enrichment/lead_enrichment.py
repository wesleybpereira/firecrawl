#!/usr/bin/env python3
"""
Firecrawl + Gemini Lead Enrichment Tool
Enriquece leads encontrando sites oficiais, telefones, emails e CNPJs através de busca web
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv
import google.genai as genai

# Carregar variáveis de ambiente
load_dotenv()

# Cores ANSI para output colorido
class Colors:
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

@dataclass
class LeadData:
    """Estrutura de dados para informações do lead"""
    empresa: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    row_number: Optional[int] = None
    is_corporate_email: str = "false"
    domain: str = ""

@dataclass
class EnrichedLead:
    """Estrutura de dados para lead enriquecido"""
    original_data: LeadData
    website: Optional[str] = None
    additional_phones: List[str] = None
    additional_emails: List[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    redes_sociais: Dict[str, str] = None
    confidence_score: float = 0.0
    search_results_used: List[str] = None

class LeadEnrichmentService:
    """Serviço principal para enriquecimento de leads usando Firecrawl + Gemini"""
    
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.firecrawl_internal_url = os.getenv("FIRECRAWL_INTERNAL_URL")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Para self-hosted, pode usar URL interna ou API key
        if not self.firecrawl_api_key and not self.firecrawl_internal_url:
            raise ValueError("Configure FIRECRAWL_API_KEY ou FIRECRAWL_INTERNAL_URL nas variáveis de ambiente")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")
        
        # Inicializar cliente Gemini
        self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        self.model_name = "gemini-2.5-pro-exp-03-25"
        
        # Configurar base URL do Firecrawl
        if self.firecrawl_internal_url:
            self.firecrawl_base_url = self.firecrawl_internal_url.rstrip('/')
            print(f"{Colors.CYAN}🔗 Usando Firecrawl interno: {self.firecrawl_base_url}{Colors.RESET}")
        else:
            self.firecrawl_base_url = "https://api.firecrawl.dev"
            print(f"{Colors.CYAN}🔗 Usando Firecrawl cloud: {self.firecrawl_base_url}{Colors.RESET}")
        
        # Headers para Firecrawl
        self.firecrawl_headers = {
            'Content-Type': 'application/json'
        }
        
        if self.firecrawl_api_key:
            self.firecrawl_headers['Authorization'] = f'Bearer {self.firecrawl_api_key}'
    
    def search_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações da empresa usando Firecrawl search (SearXNG)
        """
        print(f"{Colors.YELLOW}🔍 Buscando informações para: {company_name}{Colors.RESET}")
        
        payload = {
            "query": company_name,
            "limit": 10  # Limitar resultados para processar mais rápido
        }
        
        try:
            response = requests.post(
                f"{self.firecrawl_base_url}/v1/search",
                headers=self.firecrawl_headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                print(f"{Colors.RED}❌ Erro na busca: {data.get('error', 'Erro desconhecido')}{Colors.RESET}")
                return None
            
            search_data = data.get('data', {})
            web_results = search_data.get('web', [])
            
            if not web_results:
                print(f"{Colors.RED}❌ Nenhum resultado encontrado para: {company_name}{Colors.RESET}")
                return None
            
            print(f"{Colors.GREEN}✅ Encontrados {len(web_results)} resultados{Colors.RESET}")
            return search_data
            
        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}❌ Erro na requisição de busca: {str(e)}{Colors.RESET}")
            return None
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}❌ Erro ao decodificar resposta JSON: {str(e)}{Colors.RESET}")
            return None
    
    def analyze_search_results_with_gemini(self, search_data: Dict[str, Any], company_name: str) -> Optional[Dict[str, Any]]:
        """
        Usa Gemini para analisar os resultados de busca e extrair informações relevantes
        """
        print(f"{Colors.YELLOW}🤖 Analisando resultados com Gemini...{Colors.RESET}")
        
        web_results = search_data.get('web', [])
        
        # Preparar dados para análise
        search_results_text = []
        for result in web_results:
            result_text = f"URL: {result.get('url', '')}\n"
            result_text += f"Título: {result.get('title', '')}\n"
            result_text += f"Descrição: {result.get('description', '')}\n"
            result_text += "---\n"
            search_results_text.append(result_text)
        
        search_content = "\n".join(search_results_text)
        
        prompt = f"""
Você é um especialista em enriquecimento de leads e análise de dados empresariais.

Analise os seguintes resultados de busca para a empresa "{company_name}" e extraia as informações mais relevantes e confiáveis.

RESULTADOS DA BUSCA:
{search_content}

TAREFA:
Encontre e extraia as seguintes informações da empresa "{company_name}":

1. Site oficial (URL mais provável de ser o site oficial da empresa)
2. Telefones adicionais (diferentes do original, se houver)
3. Emails corporativos adicionais
4. CNPJ (se mencionado)
5. Endereço completo
6. Redes sociais (Instagram, Facebook, LinkedIn, etc.)
7. Score de confiança (0-100) baseado na qualidade e consistência das informações

INSTRUÇÕES IMPORTANTES:
- Priorize sempre o site oficial da empresa (domínio próprio)
- Ignore redes sociais como site principal, mas inclua nas redes sociais
- Extraia apenas informações que parecem confiáveis e consistentes
- Se não encontrar uma informação, deixe como null
- Telefones devem estar no formato brasileiro (com DDD)
- Emails devem ser corporativos quando possível

FORMATO DE RESPOSTA:
Retorne APENAS um objeto JSON válido no seguinte formato:

{{
    "website": "https://exemplo.com.br",
    "additional_phones": ["(48) 99999-9999", "(48) 3333-4444"],
    "additional_emails": ["contato@empresa.com.br", "vendas@empresa.com.br"],
    "cnpj": "00.000.000/0001-00",
    "endereco": "Rua Exemplo, 123, Bairro, Cidade - UF, CEP",
    "redes_sociais": {{
        "instagram": "https://instagram.com/empresa",
        "facebook": "https://facebook.com/empresa",
        "linkedin": "https://linkedin.com/company/empresa"
    }},
    "confidence_score": 85,
    "search_results_used": ["https://site1.com", "https://site2.com"]
}}

Responda APENAS com o JSON, sem texto adicional.
"""

        try:
            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Limpar a resposta
            response_text = response.text.strip()
            
            # Remover markdown se presente
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                # Remover primeira linha (```json ou ```)
                lines = lines[1:]
                # Remover última linha se for ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines)
            
            # Parsear JSON
            try:
                result = json.loads(response_text)
                print(f"{Colors.GREEN}✅ Análise concluída com sucesso{Colors.RESET}")
                return result
                
            except json.JSONDecodeError as e:
                print(f"{Colors.RED}❌ Erro ao parsear JSON da resposta do Gemini: {str(e)}{Colors.RESET}")
                print(f"{Colors.MAGENTA}Resposta recebida: {response_text}{Colors.RESET}")
                return None
                
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao analisar com Gemini: {str(e)}{Colors.RESET}")
            return None
    
    def enrich_lead(self, lead_data: LeadData) -> Optional[EnrichedLead]:
        """
        Enriquece um lead com informações adicionais
        """
        print(f"{Colors.CYAN}🚀 Iniciando enriquecimento do lead: {lead_data.empresa}{Colors.RESET}")
        
        # Buscar informações da empresa
        search_data = self.search_company(lead_data.empresa)
        if not search_data:
            return None
        
        # Analisar resultados com Gemini
        analysis_result = self.analyze_search_results_with_gemini(search_data, lead_data.empresa)
        if not analysis_result:
            return None
        
        # Criar lead enriquecido
        enriched_lead = EnrichedLead(
            original_data=lead_data,
            website=analysis_result.get('website'),
            additional_phones=analysis_result.get('additional_phones', []),
            additional_emails=analysis_result.get('additional_emails', []),
            cnpj=analysis_result.get('cnpj'),
            endereco=analysis_result.get('endereco'),
            redes_sociais=analysis_result.get('redes_sociais', {}),
            confidence_score=analysis_result.get('confidence_score', 0.0),
            search_results_used=analysis_result.get('search_results_used', [])
        )
        
        return enriched_lead
    
    def enrich_lead_from_json(self, lead_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enriquece um lead a partir de um objeto JSON (compatível com N8N)
        """
        # Converter JSON para LeadData
        lead_data = LeadData(
            empresa=lead_json.get('empresa', ''),
            telefone=lead_json.get('telefone'),
            email=lead_json.get('email'),
            row_number=lead_json.get('row_number'),
            is_corporate_email=lead_json.get('is_corporate_email', 'false'),
            domain=lead_json.get('domain', '')
        )
        
        # Enriquecer lead
        enriched = self.enrich_lead(lead_data)
        if not enriched:
            return None
        
        # Converter para JSON para compatibilidade com N8N
        result = {
            "original_data": {
                "empresa": enriched.original_data.empresa,
                "telefone": enriched.original_data.telefone,
                "email": enriched.original_data.email,
                "row_number": enriched.original_data.row_number,
                "is_corporate_email": enriched.original_data.is_corporate_email,
                "domain": enriched.original_data.domain
            },
            "enriched_data": {
                "website": enriched.website,
                "additional_phones": enriched.additional_phones,
                "additional_emails": enriched.additional_emails,
                "cnpj": enriched.cnpj,
                "endereco": enriched.endereco,
                "redes_sociais": enriched.redes_sociais,
                "confidence_score": enriched.confidence_score,
                "search_results_used": enriched.search_results_used
            }
        }
        
        return result

def main():
    """Função principal para teste da aplicação"""
    service = LeadEnrichmentService()
    
    # Exemplo de uso com dados fornecidos
    example_lead = {
        "empresa": "MARISTELA MODA PET",
        "telefone": "4833655751",
        "email": "maristelamodapet@hotmail.com",
        "row_number": 2,
        "is_corporate_email": "false",
        "domain": ""
    }
    
    print(f"{Colors.BLUE}🎯 Testando com lead de exemplo:{Colors.RESET}")
    print(json.dumps(example_lead, indent=2, ensure_ascii=False))
    print()
    
    # Enriquecer lead
    result = service.enrich_lead_from_json(example_lead)
    
    if result:
        print(f"{Colors.GREEN}✅ Lead enriquecido com sucesso!{Colors.RESET}")
        print(f"{Colors.CYAN}📊 Resultado:{Colors.RESET}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"{Colors.RED}❌ Falha ao enriquecer o lead{Colors.RESET}")

if __name__ == "__main__":
    main()
