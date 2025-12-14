import logging
from abc import ABC, abstractmethod
from .biophysics import BiophysicalEngine
from .clients import ClinVarClient, UniProtClient

# Configure Logger
logger = logging.getLogger(__name__)

class AnalysisStrategy(ABC):
    """
    The Interface. 
    Every 'Strategy' class MUST have an 'execute' method.
    This enforces discipline so the Router doesn't crash.
    """
    @abstractmethod
    def execute(self, context):
        pass

class HumanStrategy(AnalysisStrategy):
    """
    The 'Premium' Tier.
    Triggered when: Organism == 'Homo sapiens'
    Action: 
      1. Calculate Physics (Mass/Charge changes).
      2. Check ClinVar (Is this a known disease?).
    """
    def execute(self, context):
        logger.info(f"Executing Human Strategy for {context.get('gene', 'Unknown Gene')}")
        
        # 1. The Physics (Universal)
        # We assume context contains keys 'old_aa' and 'new_aa' (e.g., 'W' and 'R')
        physics_data = BiophysicalEngine.calculate_deltas(
            context.get('old_aa'), 
            context.get('new_aa')
        )

        # 2. The Clinical Data (Human Specific)
        # We need the gene name and the variant code (e.g., 'BRCA1', 'c.123A>T')
        clinical_data = ClinVarClient.fetch_variant_data(
            context.get('gene'), 
            context.get('variant_code')
        )
        
        return {
            "strategy_used": "HumanClinical",
            "biophysics": physics_data,
            "clinical": clinical_data,
            "functional": None # Humans rely on ClinVar, not UniProt function usually
        }

class UniversalStrategy(AnalysisStrategy):
    """
    The 'General Biologist' Tier.
    Triggered when: Organism is Dog, Virus, Bacteria, Yeast, Mouse, etc.
    Action:
      1. Calculate Physics.
      2. Check UniProt (What does this protein do in this animal?).
    """
    def execute(self, context):
        organism = context.get('organism')
        gene = context.get('gene')
        logger.info(f"Executing Universal Strategy for {organism} : {gene}")

        # 1. The Physics
        physics_data = BiophysicalEngine.calculate_deltas(
            context.get('old_aa'), 
            context.get('new_aa')
        )

        # 2. The Function (Species Specific)
        # "What does Insulin do in a Dog?"
        functional_data = UniProtClient.fetch_protein_data(organism, gene)
        
        return {
            "strategy_used": "UniversalFunctional",
            "biophysics": physics_data,
            "clinical": None, # ClinVar doesn't track Dog diseases well
            "functional": functional_data
        }

class FallbackStrategy(AnalysisStrategy):
    """
    The 'Safety Net'.
    Triggered when: Organism is Unknown or Synthetic.
    Action:
      1. Calculate Physics ONLY.
      2. Admit we don't know the biology.
    """
    def execute(self, context):
        logger.info("Executing Fallback Strategy (Biophysics Only)")

        physics_data = BiophysicalEngine.calculate_deltas(
            context.get('old_aa'), 
            context.get('new_aa')
        )

        return {
            "strategy_used": "BiophysicsOnly",
            "biophysics": physics_data,
            "clinical": None,
            "functional": {"function": "Organism unknown. Functional analysis skipped."},
            "note": "Analysis limited to physicochemical properties due to unidentified organism."
        }