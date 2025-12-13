import re
from Bio.Blast import NCBIWWW, NCBIXML
from django.conf import settings
from analysis.models import AnalysisProject, AnalysisResult

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
            # 1. Fetch the project
            project = AnalysisProject.objects.get(id=project_id)
            sequence = project.input_sequence

            # 2. Optimization: Slice the sequence
            # BLAST is slow. We only need the first 500 base pairs to identify 
            # the organism with high confidence. Sending 5MB takes too long.
            query_sequence = sequence[:500]

            print(f"Creating BLAST query for Project {project_id}...")
            
            # 3. The API Call (Heavy Network Operation)
            # program="blastn" -> Nucleotide vs Nucleotide database
            # database="nt" -> Nucleotide Collection (GenBank, EMBL, DDBJ, PDB)
            result_handle = NCBIWWW.qblast("blastn", "nt", query_sequence)

            # 4. Parse the XML Response
            blast_record = NCBIXML.read(result_handle)
            result_handle.close()

            organism = "Unknown"

            # 5. Extract Organism Name
            if blast_record.alignments:
                # The "title" usually looks like:
                # "gi|1798174254|ref|NM_007294.4| Homo sapiens BRCA1 DNA repair associated (BRCA1)..."
                top_hit_title = blast_record.alignments[0].title
                
                organism = OrganismScanner._extract_organism_name(top_hit_title)
                print(f"BLAST Success: Identified as {organism}")
            else:
                print("BLAST finished but returned no matches.")

            # 6. Save to Database
            # We use get_or_create in case the result record exists or needs creating
            analysis_result, created = AnalysisResult.objects.get_or_create(project=project)
            analysis_result.organism = organism
            analysis_result.save()

            return organism

        except Exception as e:
            print(f"BLAST Logic Error: {e}")
            # In a real app, we would log this to a file or Sentry
            return None

    @staticmethod
    def _extract_organism_name(title_string):
        """
        Helper method to pull 'Homo sapiens' out of a messy description string.
        """
        # Strategy 1: Look for scientific name inside brackets [Homo sapiens]
        # NCBI often formats titles like "Description of gene [Organism Name]"
        match = re.search(r'\[([^\]]+)\]', title_string)
        if match:
            return match.group(1)
        
        # Strategy 2: If no brackets, try to grab the first two words after the ID pipes
        # This is a fallback and might need refinement based on data observed
        # Example: "...| Homo sapiens BRCA1 ..."
        parts = title_string.split('|')
        if len(parts) > 1:
             # Take the description part (usually the last part after pipes)
            description = parts[-1].strip()
            words = description.split()
            if len(words) >= 2:
                return f"{words[0]} {words[1]}"
        
        return "Unknown Organism"