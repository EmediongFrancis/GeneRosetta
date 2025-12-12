from rest_framework import serializers
from .validators import validate_file_extension, validate_file_size
from .models import AnalysisProject

class AnalysisInputSerializer(serializers.Serializer):
    # Validators applied directly to the FileField
    sequence_file = serializers.FileField(
        required=False, 
        validators=[validate_file_extension, validate_file_size]
    )
    raw_text = serializers.CharField(required=False)

    def validate(self, data):
        """
        Check that exactly one input method is provided.
        """
        has_file = 'sequence_file' in data
        has_text = 'raw_text' in data

        if has_file and has_text:
            raise serializers.ValidationError("Please provide either a file OR raw text, not both.")
        
        if not has_file and not has_text:
            raise serializers.ValidationError("No input data provided.")

        return data