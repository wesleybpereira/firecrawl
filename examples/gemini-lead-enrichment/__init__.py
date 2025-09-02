"""
Firecrawl + Gemini Lead Enrichment
Pacote para enriquecimento de leads usando Firecrawl e Google Gemini
"""

from .lead_enrichment import LeadEnrichmentService, LeadData, EnrichedLead

__version__ = "1.0.0"
__author__ = "Firecrawl Team"

__all__ = [
    "LeadEnrichmentService",
    "LeadData", 
    "EnrichedLead"
]
