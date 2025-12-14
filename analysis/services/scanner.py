import re
import logging
from Bio.Blast import NCBIWWW, NCBIXML
from urllib.error import URLError, HTTPError
from django.core.exceptions import ObjectDoesNotExist
from analysis.models import AnalysisProject, AnalysisResult

# Configure Logger
logger = logging.getLogger(__name__)

class OrganismScanner:
    """
    Service responsible for identifying the species of a DNA sequence
    using the NCBI BLAST API.
    """

    @staticmethod
    def identify_organism(project_id):
        """
        Main entry point.
        1. Fetches project.
        2. Queries NCBI BLAST.
        3. Parses result.
        4. Updates Database.
        """
        try:
            # 1. Fetch the project (Handle Invalid ID)
            project = AnalysisProject.objects.get(id=project_id)
            
        except ObjectDoesNotExist:
            logger.error(f"Scanner Error: Project with UUID {project_id} not found.")
            return None
        except Exception as e:
            logger.critical(f"Scanner Critical Database Error: {str(e)}")
            return None

        # 2. Prepare for Analysis
        try:
            # Update status to tell user "We are working on it"
            # (Note: Celery handles this, but good to have here too)
            project.status = 'PROCESSING'
            project.save(update_fields=['status'])

            sequence = project.input_sequence
            
            # Optimization: Slice the sequence
            if len(sequence) > 500:
                query_sequence = sequence[:500]
            else:
                query_sequence = sequence

            logger.info(f"Initiating BLAST query for Project {project_id}...")
            
            # 3. The API Call (Handle Network Failures)
            try:
                result_handle = NCBIWWW.qblast("blastn", "nt", query_sequence)
            except HTTPError as e:
                logger.error(f"NCBI Server Error: {e.code}")
                OrganismScanner._mark_failed(project)
                return None
            except URLError as e:
                logger.error(f"Network Connection Failed: {str(e.reason)}")
                OrganismScanner._mark_failed(project)
                return None

            # 4. Parse the XML Response
            try:
                blast_record = NCBIXML.read(result_handle)
                result_handle.close()
            except Exception as e:
                logger.error(f"XML Parsing Failed: {str(e)}")
                OrganismScanner._mark_failed(project)
                return None

            organism = "Unknown"

            # 5. Extract Organism Name
            if blast_record.alignments:
                top_hit_title = blast_record.alignments[0].title
                organism = OrganismScanner._extract_organism_name(top_hit_title)
                gene_name = OrganismScanner._extract_gene_name(top_hit_title)
                logger.info(f"BLAST Success: Identified as {organism}")
            else:
                logger.warning(f"BLAST finished but returned no matches for Project {project_id}")

            # 6. Save to Database
            AnalysisResult.objects.update_or_create(
                project=project,
                defaults={'organism': organism}
            )

            # Note: We do NOT set status to COMPLETED here yet.
            # In the final pipeline, this is just Step 1 of 3.
            return organism, gene_name

        except Exception as e:
            logger.exception(f"Unexpected Scanner Error: {str(e)}")
            OrganismScanner._mark_failed(project)
            return None

    @staticmethod
    def _mark_failed(project):
        """Helper to safely mark project as failed so UI doesn't hang."""
        project.status = 'FAILED'
        project.save(update_fields=['status'])

    @staticmethod
    def _extract_organism_name(title_string):
        """
        Helper method to pull 'Homo sapiens' out of a messy description string.
        """
        # Strategy 1: Look for scientific name inside brackets [Homo sapiens]
        match = re.search(r'\[([^\]]+)\]', title_string)
        if match:
            return match.group(1)
        
        # Strategy 2: Fallback to first two words after pipes
        parts = title_string.split('|')
        if len(parts) > 1:
            description = parts[-1].strip()
            words = description.split()
            if len(words) >= 2:
                return f"{words[0]} {words[1]}"
        
        return "Unknown Organism"
    
    @staticmethod
    def _extract_gene_name(title_string):
        """
        Heuristic: Looks for text inside parentheses often used for gene symbols.
        Example: "...Homo sapiens insulin (INS), transcript variant..." -> Returns "INS"
        """
        # Look for (GENE) pattern
        match = re.search(r'\(([A-Z0-9]+)\)', title_string)
        if match:
            return match.group(1)
        
        # Fallback: Look for "mRNA" or "gene" and take the word before it? 
        # For now, let's return a safe default if regex fails.
        return "Unknown Gene"