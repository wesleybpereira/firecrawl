#!/bin/bash

# Script de instalação para Firecrawl + Gemini Lead Enrichment

echo "🚀 Instalando Firecrawl + Gemini Lead Enrichment..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3 primeiro."
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale pip primeiro."
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "⚙️ Criando arquivo .env..."
    cp .env.example .env
    echo "🔧 ATENÇÃO: Edite o arquivo .env com suas chaves de API!"
    echo "   - FIRECRAWL_API_KEY: obtenha em https://firecrawl.dev"
    echo "   - GEMINI_API_KEY: obtenha em https://aistudio.google.com"
fi

# Verificar se as chaves estão configuradas
if grep -q "your-api-key-here" .env; then
    echo "⚠️  AVISO: Configure suas chaves de API no arquivo .env antes de usar!"
else
    echo "✅ Arquivo .env configurado!"
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🎯 Como usar:"
echo "   python3 example.py          # Testar com exemplo"
echo "   python3 flask-server.py     # Iniciar servidor para N8N"
echo ""
echo "📚 Para mais informações, consulte o README.md"
