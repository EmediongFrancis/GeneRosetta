import uuid
from django.db import models
from django.conf import settings  # Connects Custom User

class AnalysisProject(models.Model):
    """
    The 'Ticket'. Created immediately when a user uploads data.
    """
    # ENUMS for choices
    INPUT_TYPES = (
        ('FASTA', 'FASTA File'),
        ('VCF', 'VCF File'),
        ('TEXT', 'Raw Text'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    # FIELDS
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Links to Custom User. Null=True allows Guest Mode.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    input_type = models.CharField(max_length=10, choices=INPUT_TYPES)
    input_sequence = models.TextField(help_text="The cleaned, raw DNA sequence")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.status}"

class AnalysisResult(models.Model):
    """
    The 'Outcome'. Populated by the Async Worker.
    """
    project = models.OneToOneField(
        AnalysisProject, 
        on_delete=models.CASCADE, 
        related_name='result'
    )
    
    organism = models.CharField(max_length=255, blank=True, null=True)
    pdb_data = models.TextField(blank=True, null=True, help_text="Raw PDB string for 3D rendering")
    
    # JSONField for "Mad Libs" report and biophysical data
    report = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Result for {self.project.id}"