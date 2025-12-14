import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class StructureService:
    """
    Connects to the ESMFold API (by Meta AI) to predict 3D protein structures.
    """
    API_URL = "https://api.esmatlas.com/foldSequence/v1/pdb/"

    @staticmethod
    def generate_pdb(sequence):
        """
        Input: Amino acid sequence string.
        Output: PDB format string (3D coordinates).
        """
        # Safety Check: ESMFold has a limit (usually ~400 residues for the public API).
        # We slice it to ensure we don't crash.
        if len(sequence) > 400:
            logger.warning("Sequence too long for ESMFold. Truncating to 400 residues.")
            sequence = sequence[:400]

        try:
            logger.info(f"Requesting structure for sequence length {len(sequence)}...")
            response = requests.post(StructureService.API_URL, data=sequence, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"ESMFold API Error {response.status_code}: {response.text}")
                return None
                
            # The API returns the raw PDB text body.
            return response.text

        except Exception as e:
            logger.error(f"Structure Generation Failed: {str(e)}")
            return None