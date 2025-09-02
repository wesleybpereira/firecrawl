#!/usr/bin/env python3
"""
Servidor Flask para integração com N8N
Fornece uma API REST para enriquecimento de leads
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback

# Adicionar o diretório atual ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from lead_enrichment import LeadEnrichmentService
except ImportError as e:
    print(f"Erro ao importar LeadEnrichmentService: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Permitir CORS para integração com N8N

# Inicializar o serviço
try:
    service = LeadEnrichmentService()
    print("✅ Serviço de enriquecimento inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar serviço: {e}")
    sys.exit(1)

@app.route('/', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "ok",
        "service": "Firecrawl + Gemini Lead Enrichment",
        "version": "1.0.0"
    })

@app.route('/enrich-lead', methods=['POST'])
def enrich_lead():
    """
    Endpoint principal para enriquecimento de leads
    
    Payload esperado:
    {
        "empresa": "Nome da Empresa",
        "telefone": "opcional",
        "email": "opcional", 
        "row_number": "opcional",
        "is_corporate_email": "opcional",
        "domain": "opcional"
    }
    """
    try:
        # Validar se o request contém JSON
        if not request.is_json:
            return jsonify({
                "error": "Content-Type deve ser application/json"
            }), 400
        
        lead_data = request.get_json()
        
        # Validar campos obrigatórios
        if not lead_data or not lead_data.get('empresa'):
            return jsonify({
                "error": "Campo 'empresa' é obrigatório"
            }), 400
        
        # Enriquecer o lead
        result = service.enrich_lead_from_json(lead_data)
        
        if result:
            return jsonify({
                "success": True,
                "data": result
            })
        else:
            return jsonify({
                "success": False,
                "error": "Não foi possível enriquecer o lead",
                "data": None
            }), 404
            
    except Exception as e:
        # Log do erro completo
        error_trace = traceback.format_exc()
        print(f"❌ Erro ao processar request: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}",
            "data": None
        }), 500

@app.route('/enrich-batch', methods=['POST'])
def enrich_batch():
    """
    Endpoint para enriquecimento em lote
    
    Payload esperado:
    {
        "leads": [
            {
                "empresa": "Empresa 1",
                "telefone": "...",
                ...
            },
            {
                "empresa": "Empresa 2", 
                "telefone": "...",
                ...
            }
        ]
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type deve ser application/json"
            }), 400
        
        data = request.get_json()
        leads = data.get('leads', [])
        
        if not leads or not isinstance(leads, list):
            return jsonify({
                "error": "Campo 'leads' deve ser uma lista não vazia"
            }), 400
        
        results = []
        
        for i, lead_data in enumerate(leads):
            try:
                if not lead_data.get('empresa'):
                    results.append({
                        "index": i,
                        "success": False,
                        "error": "Campo 'empresa' é obrigatório",
                        "data": None
                    })
                    continue
                
                result = service.enrich_lead_from_json(lead_data)
                
                results.append({
                    "index": i,
                    "success": True if result else False,
                    "error": None if result else "Não foi possível enriquecer o lead",
                    "data": result
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e),
                    "data": None
                })
        
        # Estatísticas do lote
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return jsonify({
            "success": True,
            "batch_stats": {
                "total": len(results),
                "successful": successful,
                "failed": failed
            },
            "results": results
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Erro ao processar lote: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": f"Erro interno do servidor: {str(e)}",
            "data": None
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint não encontrado"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Erro interno do servidor"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando servidor Flask em {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📡 Endpoints disponíveis:")
    print(f"   GET  / - Health check")
    print(f"   POST /enrich-lead - Enriquecer lead único")  
    print(f"   POST /enrich-batch - Enriquecer lote de leads")
    
    # Verificar se as variáveis de ambiente estão configuradas
    if not os.getenv('FIRECRAWL_API_KEY'):
        print("⚠️  AVISO: FIRECRAWL_API_KEY não configurada")
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  AVISO: GEMINI_API_KEY não configurada")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
