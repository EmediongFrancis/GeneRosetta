import requests # type: ignore
import logging
from Bio import Entrez

# Configure Logging
logger = logging.getLogger(__name__)

# IMPORTANT: NCBI requires you to provide an email so they can contact you 
# if your script accidentally spams their server.
Entrez.email = "emediongfrancis@gmail.com" 

class ClinVarClient:
    """
    The 'Doctor'. 
    Talks to the NCBI ClinVar database to see if a human mutation causes disease.
    """
    
    @staticmethod
    def fetch_variant_data(gene_name, variant_code):
        """
        Uses NCBI E-utilities to find clinical significance.
        Input: Gene="BRCA1", Variant="c.123A>T" (or protein change)
        """
        try:
            # 1. Construct a Search Query
            # We look for the Gene AND the specific mutation string.
            search_term = f"{gene_name}[Gene Name] AND {variant_code}[Text Word]"
            logger.info(f"ClinVar Search: {search_term}")

            # 2. E-Search: Find the ID of the record
            handle = Entrez.esearch(db="clinvar", term=search_term, retmax=1)
            record = Entrez.read(handle)
            handle.close()

            id_list = record['IdList'] # type: ignore

            if not id_list:
                logger.warning("ClinVar: No matching record found.")
                return {"significance": "Unknown / Not Listed in ClinVar"}

            # 3. E-Summary: Get the details for that ID
            clinvar_id = id_list[0]
            summary_handle = Entrez.esummary(db="clinvar", id=clinvar_id)
            summary_record = Entrez.read(summary_handle)
            summary_handle.close()

            # 4. Parse the Result
            # The structure of the response is messy. We look for 'clinical_significance'.
            data = summary_record['DocumentSummarySet']['DocumentSummary'][0] # type: ignore
            significance = data.get('clinical_significance', {}).get('description', 'Unknown')
            disease_name = data.get('trait_set', [{}])[0].get('trait_name', 'Unspecified Condition')

            return {
                "significance": significance, # e.g., "Pathogenic", "Benign"
                "disease": disease_name,      # e.g., "Breast Cancer"
                "clinvar_id": clinvar_id
            }

        except Exception as e:
            logger.error(f"ClinVar API Error: {e}")
            return {"significance": "Error connecting to Clinical Database"}


class UniProtClient:
    """
    The 'Biologist'.
    Talks to the UniProt Knowledgebase to find out what a protein DOES.
    Works for any species (Dog, Virus, Bacteria).
    """

    BASE_URL = "https://rest.uniprot.org/uniprotkb/search"

    @staticmethod
    def fetch_protein_data(organism_name, gene_name):
        """
        Input: Organism="Canis lupus familiaris", Gene="INS"
        Output: "Insulin decreases blood glucose concentration..."
        """
        try:
            # 1. Construct the API Query
            # query = (gene:INS) AND (organism_id:9615 OR organism_name:"Canis lupus")
            query = f"gene:{gene_name} AND organism_name:\"{organism_name}\""
            
            params = {
                "query": query,
                "format": "json",
                "fields": "cc_function", # We only want the 'Function' comment
                "size": 1 # Just give us the best match
            }

            logger.info(f"UniProt Search: {query}")

            # 2. Make the HTTP Request
            response = requests.get(UniProtClient.BASE_URL, params=params, timeout=10)
            response.raise_for_status() # Raise error if 404/500

            data = response.json()

            # 3. Parse the JSON
            if not data['results']:
                return {"function": "No functional data found for this protein."}

            # Dive into the JSON structure to find the "Function" comment
            result = data['results'][0]
            comments = result.get('comments', [])
            
            function_text = "Function description unavailable."
            
            for comment in comments:
                if comment['commentType'] == 'FUNCTION':
                    # Extract the actual text description
                    function_text = comment['texts'][0]['value']
                    break

            return {
                "function": function_text,
                "uniprot_id": result.get('primaryAccession')
            }

        except Exception as e:
            logger.error(f"UniProt API Error: {e}")
            return {"function": "Error connecting to Protein Database"}