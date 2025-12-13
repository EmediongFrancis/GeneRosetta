from celery import shared_task
from .services.scanner import OrganismScanner
from .models import AnalysisProject
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_analysis_pipeline(project_id):
    """
    Background task to run the full analysis pipeline.
    """
    logger.info(f"Background Task Started: Processing Project {project_id}")
    
    try:
        # 1. Update status to PROCESSING
        # We use .update() to avoid race conditions with fetching the object
        AnalysisProject.objects.filter(id=project_id).update(status='PROCESSING')

        # 2. Run the Scanner
        organism = OrganismScanner.identify_organism(project_id)
        
        if organism:
            # Success
            logger.info(f"Background Task Success: Identified {organism}")
            AnalysisProject.objects.filter(id=project_id).update(status='COMPLETED')
        else:
            # Failure (Scanner returned None)
            logger.error(f"Background Task Failed: Scanner returned None")
            AnalysisProject.objects.filter(id=project_id).update(status='FAILED')

    except Exception as e:
        logger.exception(f"CRITICAL WORKER ERROR: {str(e)}")
        AnalysisProject.objects.filter(id=project_id).update(status='FAILED')