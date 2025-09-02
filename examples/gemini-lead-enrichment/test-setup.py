#!/usr/bin/env python3
"""
Teste de importações e conectividade
"""

import sys
import os

def test_imports():
    """Testa todas as importações necessárias"""
    try:
        print("🧪 Testando importações...")
        
        # Teste básico
        import requests
        print("✅ requests: OK")
        
        import json
        print("✅ json: OK")
        
        # Teste dotenv
        from dotenv import load_dotenv
        print("✅ python-dotenv: OK")
        
        # Teste Flask
        from flask import Flask
        print("✅ flask: OK")
        
        # Teste Google Generative AI
        import google.generativeai as genai
        print("✅ google-generativeai: OK")
        
        print("\n🎉 Todas as importações funcionando!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_gemini_connection():
    """Testa conexão com Gemini"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️  GEMINI_API_KEY não configurada - pulando teste de conexão")
            return True
            
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content("Responda apenas: OK")
        
        if "OK" in response.text:
            print("✅ Conexão com Gemini: OK")
            return True
        else:
            print("⚠️  Conexão com Gemini: Resposta inesperada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão com Gemini: {e}")
        return False

def test_firecrawl_internal():
    """Testa conexão interna com Firecrawl"""
    try:
        import requests
        
        # Tentar conectar com URL interna
        internal_url = os.getenv('FIRECRAWL_INTERNAL_URL', 'http://api:3002')
        response = requests.get(f"{internal_url}/test", timeout=5)
        
        if response.status_code == 200:
            print("✅ Conexão interna Firecrawl: OK")
            return True
        else:
            print(f"⚠️  Conexão interna Firecrawl: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Conexão interna Firecrawl: Não disponível (normal durante build)")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão interna: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Diagnóstico do Lead Enrichment Service")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    all_passed = True
    
    # Teste de importações
    if not test_imports():
        all_passed = False
    
    print()
    
    # Teste de conexão Gemini
    if not test_gemini_connection():
        all_passed = False
    
    print()
    
    # Teste de conexão Firecrawl
    if not test_firecrawl_internal():
        all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam")
        sys.exit(1)
