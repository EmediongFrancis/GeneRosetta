import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    """
    Ensures the file ends with .fasta, .txt, or .vcf.
    """
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.fasta', '.txt', '.vcf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed: .fasta, .txt, .vcf')

def validate_file_size(value):
    """
    Limits file size to 50KB to prevent server overload.
    """
    limit = 50 * 1024  # 50 KB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 50 KB.')