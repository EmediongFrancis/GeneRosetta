from celery import shared_task
import logging
from Bio.Seq import Seq
from .services.scanner import OrganismScanner
from .engine.router import get_strategy
# Import UniversalStrategy specifically for the "Normal Gene" override
from .engine.strategies import UniversalStrategy 
from .engine.narrative import NarrativeComposer
from .services.structure import StructureService
from .models import AnalysisProject, AnalysisResult

logger = logging.getLogger(__name__)

@shared_task
def run_analysis_pipeline(project_id):
    logger.info(f"Pipeline Started: Project {project_id}")
    
    try:
        project = AnalysisProject.objects.get(id=project_id)
        project.status = 'PROCESSING'
        project.save()

        # STEP 1: Identification (Scanner)
        # We handle cases where Scanner might return a tuple (New) or string (Old)
        scan_result = OrganismScanner.identify_organism(project_id)
        
        if isinstance(scan_result, tuple):
            organism, gene_name = scan_result
        else:
            organism = scan_result
            gene_name = "Unknown Gene"

        # STEP 2: Translation (DNA -> Protein)
        dna_sequence = Seq(project.input_sequence)
        # Translate to protein, stopping at the first stop codon
        protein_sequence = str(dna_sequence.translate(to_stop=True))
        
        logger.info(f"Translated DNA to Protein: {protein_sequence[:20]}...")

        # STEP 3: Smart Context Construction
        # We explicitly set old_aa/new_aa to None. 
        # This signals to the engine: "This is a healthy gene, not a mutation."
        context = {
            "organism": organism,
            "gene": gene_name,
            "old_aa": None,     
            "new_aa": None      
        }
        
        # STEP 4: Strategy Selection
        # LOGIC: If we found a specific gene (e.g., "INS") but have no mutation data,
        # we want to know what the gene DOES (Function), not what disease it causes.
        # So we override the Router and use the UniversalStrategy (UniProt).
        if gene_name and gene_name != "Unknown Gene":
            logger.info(f"Gene '{gene_name}' detected. Switching to UniversalStrategy for Functional Analysis.")
            strategy = UniversalStrategy()
        else:
            # Otherwise, use the Router (Human->ClinVar, Other->UniProt)
            strategy = get_strategy(organism) # type: ignore

        strategy_result = strategy.execute(context)
        
        # STEP 5: Structure Generation (Using Protein Sequence)
        pdb_data = StructureService.generate_pdb(protein_sequence)

        # STEP 6: Narrative Generation
        final_report_text = NarrativeComposer.generate_report(strategy_result)

        # STEP 7: Save Everything
        result, _ = AnalysisResult.objects.get_or_create(project=project)
        
        result.organism = organism # Ensure organism is saved to Result model too
        result.report = {
            "text": final_report_text,
            "data": strategy_result
        }
        result.pdb_data = pdb_data
        result.save()
        
        project.status = 'COMPLETED'
        project.save()
        logger.info("Pipeline Finished Successfully.")

    except Exception as e:
        logger.error(f"Pipeline Failed: {e}")
        # Use update() to prevent race conditions
        AnalysisProject.objects.filter(id=project_id).update(status='FAILED')