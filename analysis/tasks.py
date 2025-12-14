from celery import shared_task
import logging
from .services.scanner import OrganismScanner
from .engine.router import get_strategy
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
        organism = OrganismScanner.identify_organism(project_id)
        # (Scanner updates project.organism automatically)
        
        # STEP 2: Logic Strategy
        # Note: In a real app, we would parse the Gene/Variant from the input file here.
        # For this stage of the MVP, we will MOCK the gene context or extract simple ones.
        # Let's assume for the MVP we treat the input as a simple protein sequence for structure
        # and use a fallback context for the narrative if parsing fails.
        
        # Mock Context construction (To be replaced by File Parser later)
        # This allows the pipeline to run even if we don't have a sophisticated file parser yet.
        context = {
            "organism": organism,
            "gene": "Unknown", # Placeholder
            "old_aa": "A",     # Placeholder
            "new_aa": "A"      # Placeholder
        }
        
        strategy = get_strategy(organism) # type: ignore
        strategy_result = strategy.execute(context)
        
        # STEP 3: Structure Generation
        # We assume the input_sequence is an Amino Acid string for ESMFold.
        # If it is DNA, we would need to translate it first (using Biopython .translate()).
        # For safety, let's try to generate structure from the input.
        pdb_data = StructureService.generate_pdb(project.input_sequence)

        # STEP 4: Narrative Generation
        final_report_text = NarrativeComposer.generate_report(strategy_result)

        # STEP 5: Save Everything
        # We get the existing result (created by Scanner) or create new
        result, _ = AnalysisResult.objects.get_or_create(project=project)
        
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
        AnalysisProject.objects.filter(id=project_id).update(status='FAILED')