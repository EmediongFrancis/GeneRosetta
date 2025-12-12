import io
import re
from Bio import SeqIO
from django.core.exceptions import ValidationError

class IngestService:
    @staticmethod
    def process(validated_data):
        """
        Orchestrates the extraction and cleaning of DNA data.
        Returns: A clean, uppercase string of nucleotides.
        """
        sequence_data = ""

        # PATH A: File Upload
        if 'sequence_file' in validated_data:
            uploaded_file = validated_data['sequence_file']
            
            # Read the file content. 
            # Django uploads are bytes, so we decode to string.
            file_content = uploaded_file.read().decode('utf-8')
            
            if uploaded_file.name.endswith('.fasta'):
                # Biopython requires a file-like object, so we wrap the string in StringIO
                string_io = io.StringIO(file_content)
                # Parse FASTA and grab the first sequence found
                records = list(SeqIO.parse(string_io, "fasta"))
                if not records:
                    raise ValidationError("Invalid FASTA format: No sequence found.")
                sequence_data = str(records[0].seq)
            else:
                # Treat .txt or .vcf as raw text for now (parsing VCF is complex, 
                # we assume simple variant lists or raw extraction for Tier 1)
                sequence_data = file_content

        # PATH B: Raw Text
        elif 'raw_text' in validated_data:
            sequence_data = validated_data['raw_text']

        # COMMON: Sanitization & Validation
        return IngestService._sanitize_and_validate(sequence_data)

    @staticmethod
    def _sanitize_and_validate(sequence):
        """
        Internal method to clean and check the string.
        """
        # 1. Remove whitespace, newlines, tabs
        clean_seq = "".join(sequence.split()).upper()

        # 2. Strict Regex Check: Only A, C, G, T, or N (unknown) allowed.
        # This prevents SQL injection or processing garbage data.
        dna_pattern = re.compile(r'^[ACGTN]+$')
        
        if not dna_pattern.match(clean_seq):
            raise ValidationError("Invalid DNA sequence detected. Only A, C, G, T, and N are allowed.")
        
        return clean_seq