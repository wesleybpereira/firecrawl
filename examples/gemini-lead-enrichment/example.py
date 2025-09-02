#!/usr/bin/env python3
"""
Exemplo de uso da ferramenta de enriquecimento de leads
"""

import json
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_enrichment import LeadEnrichmentService

def test_single_lead():
    """Testa o enriquecimento de um lead único"""
    print("🧪 Testando enriquecimento de lead único\n")
    
    # Criar instância do serviço
    service = LeadEnrichmentService()
    
    # Lead de exemplo (o mesmo que você forneceu)
    example_lead = {
        "empresa": "MARISTELA MODA PET",
        "telefone": "4833655751",
        "email": "maristelamodapet@hotmail.com",
        "row_number": 2,
        "is_corporate_email": "false",
        "domain": ""
    }
    
    print("📥 Dados de entrada:")
    print(json.dumps(example_lead, indent=2, ensure_ascii=False))
    print("\n" + "="*50 + "\n")
    
    # Enriquecer o lead
    result = service.enrich_lead_from_json(example_lead)
    
    if result:
        print("✅ Lead enriquecido com sucesso!")
        print("\n📤 Dados de saída:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Mostrar estatísticas
        enriched = result['enriched_data']
        print(f"\n📊 Estatísticas:")
        print(f"   🌐 Site encontrado: {'✅' if enriched.get('website') else '❌'}")
        print(f"   📞 Telefones adicionais: {len(enriched.get('additional_phones', []))}")
        print(f"   📧 Emails adicionais: {len(enriched.get('additional_emails', []))}")
        print(f"   🏢 CNPJ encontrado: {'✅' if enriched.get('cnpj') else '❌'}")
        print(f"   📍 Endereço encontrado: {'✅' if enriched.get('endereco') else '❌'}")
        print(f"   📱 Redes sociais: {len(enriched.get('redes_sociais', {}))}")
        print(f"   🎯 Score de confiança: {enriched.get('confidence_score', 0)}/100")
        
    else:
        print("❌ Falha ao enriquecer o lead")

def test_batch_leads():
    """Testa o enriquecimento de múltiplos leads"""
    print("\n🧪 Testando enriquecimento em lote\n")
    
    service = LeadEnrichmentService()
    
    # Múltiplos leads de exemplo
    leads = [
        {
            "empresa": "MARISTELA MODA PET",
            "telefone": "4833655751",
            "email": "maristelamodapet@hotmail.com",
            "row_number": 2,
            "is_corporate_email": "false",
            "domain": ""
        },
        {
            "empresa": "Empresa Inexistente XYZ123",
            "telefone": "48999999999",
            "email": "teste@gmail.com",
            "row_number": 3,
            "is_corporate_email": "false",
            "domain": ""
        }
    ]
    
    results = []
    
    for i, lead in enumerate(leads):
        print(f"🔄 Processando lead {i+1}/{len(leads)}: {lead['empresa']}")
        result = service.enrich_lead_from_json(lead)
        results.append({
            "index": i,
            "original": lead,
            "enriched": result,
            "success": result is not None
        })
    
    # Estatísticas do lote
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n📊 Estatísticas do lote:")
    print(f"   📋 Total processado: {len(results)}")
    print(f"   ✅ Sucessos: {successful}")
    print(f"   ❌ Falhas: {failed}")
    print(f"   📈 Taxa de sucesso: {(successful/len(results)*100):.1f}%")

def show_usage():
    """Mostra como usar a ferramenta"""
    print("""
🔧 Como usar a ferramenta de enriquecimento de leads:

1️⃣ Configuração inicial:
   cp .env.example .env
   # Edite o .env com suas chaves de API
   pip install -r requirements.txt

2️⃣ Uso direto em Python:
   python example.py

3️⃣ Servidor Flask para N8N:
   python flask-server.py

4️⃣ Endpoints disponíveis:
   GET  / - Health check
   POST /enrich-lead - Enriquecer lead único
   POST /enrich-batch - Enriquecer lote de leads

5️⃣ Exemplo de payload para /enrich-lead:
   {
       "empresa": "Nome da Empresa",
       "telefone": "opcional",
       "email": "opcional",
       "row_number": "opcional",
       "is_corporate_email": "opcional",
       "domain": "opcional"
   }

6️⃣ Integração com N8N:
   - Use HTTP Request node
   - Method: POST
   - URL: http://localhost:5000/enrich-lead
   - Body: JSON com dados do lead
""")

def main():
    """Função principal"""
    print("🚀 Ferramenta de Enriquecimento de Leads - Firecrawl + Gemini")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            show_usage()
            return
        elif sys.argv[1] == "--batch":
            test_batch_leads()
            return
    
    try:
        test_single_lead()
    except KeyboardInterrupt:
        print("\n\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
