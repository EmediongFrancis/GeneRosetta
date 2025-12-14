from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .serializers import AnalysisInputSerializer
from .services.ingest import IngestService
from .models import AnalysisProject
from .tasks import run_analysis_pipeline
from django.shortcuts import get_object_or_404, render

def index(request):
    recent_projects = []
    if request.user.is_authenticated:
        # Fetch last 3 completed projects for this user
        recent_projects = AnalysisProject.objects.filter(
            user=request.user, 
            status='COMPLETED'
        ).order_by('-created_at')[:3]
        
    return render(request, 'index.html', {'recent_projects': recent_projects})
class AnalyzeView(APIView):
    """
    POST /api/analyze/
    Accepts FASTA/VCF file OR raw text.
    Returns: UUID of the created project.
    """
    def post(self, request):
        serializer = AnalysisInputSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # 1. Call the Service Layer to get clean data
                clean_sequence = IngestService.process(serializer.validated_data)
                
                # 2. Determine input type for DB record
                input_type = 'TEXT'
                if 'sequence_file' in serializer.validated_data: # type: ignore
                    fname = serializer.validated_data['sequence_file'].name.lower() # type: ignore
                    if fname.endswith('.fasta'): input_type = 'FASTA'
                    elif fname.endswith('.vcf'): input_type = 'VCF'

                # 3. Create the Database Record
                # We handle the User if they are logged in, otherwise None (Guest)
                user = request.user if request.user.is_authenticated else None
                
                project = AnalysisProject.objects.create(
                    user=user,
                    input_type=input_type,
                    input_sequence=clean_sequence,
                    status='PENDING'
                )

                # 4. Trigger the Background Task
                run_analysis_pipeline.delay(project.id)

                # 5. Return the UUID "Receipt"
                return Response({
                    "id": project.id,
                    "status": project.status,
                    "message": "DNA sequence accepted. Processing pending."
                }, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                # Catch errors from the Service layer (e.g. Invalid DNA chars)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProjectStatusView(APIView):
    """
    GET /api/status/{uuid}/
    Poll this endpoint to check progress.
    """
    def get(self, request, project_id):
        project = get_object_or_404(AnalysisProject, id=project_id)
        
        data = {
            "id": project.id,
            "status": project.status,
            "organism": None,
            "pdb_data": None,
            "report": None
        }
        
        if hasattr(project, 'result'):
            data['organism'] = project.result.organism # type: ignore
            # ONLY return heavy data if completed
            if project.status == 'COMPLETED':
                data['pdb_data'] = project.result.pdb_data # type: ignore
                data['report'] = project.result.report # type: ignore

        return Response(data)    