import logging
from .strategies import (
    AnalysisStrategy, 
    HumanStrategy, 
    UniversalStrategy, 
    FallbackStrategy
)

# Configure Logger
logger = logging.getLogger(__name__)

def get_strategy(organism_name: str) -> AnalysisStrategy:
    """
    The Factory Function (The Switchboard).
    
    Decides which analysis pipeline to run based on the organism name
    detected by the Scanner (BLAST).
    
    Args:
        organism_name (str): e.g., "Homo sapiens", "Canis lupus", "Unknown"
        
    Returns:
        An instance of a class inheriting from AnalysisStrategy.
    """
    
    # 1. Safety Check: If Scanner failed and passed None/Empty string
    if not organism_name:
        logger.warning("Router received empty organism name. Using Fallback.")
        return FallbackStrategy()

    # 2. Normalize: Convert "Homo Sapiens" to "homo sapiens" to avoid case errors
    name_lower = organism_name.lower()

    # 3. Path A: Human (The Clinical Path)
    # We look for the substring because BLAST might return 
    # "Homo sapiens isolate 4..." or "Homo sapiens neanderthalensis"
    if "homo sapiens" in name_lower:
        logger.info("Router: Selected HumanStrategy")
        return HumanStrategy()

    # 4. Path B: Garbage / Synthetic (The Safety Net)
    # If BLAST says "Synthetic construct" or "Cloning vector" or "Unknown"
    if "unknown" in name_lower or "synthetic" in name_lower or "vector" in name_lower:
        logger.info("Router: Selected FallbackStrategy (Non-biological input)")
        return FallbackStrategy()

    # 5. Path C: The Universal Bucket (Dogs, Viruses, Bacteria, Yeast)
    # If it is NOT human, and NOT garbage, it is a biological organism.
    # The UniversalStrategy uses UniProt, which handles ALL biology.
    logger.info(f"Router: Selected UniversalStrategy for '{organism_name}'")
    return UniversalStrategy()