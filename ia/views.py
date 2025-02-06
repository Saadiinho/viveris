from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from .utils import waste_classifier
from .models import WasteClassification
from .serializers import WasteClassificationSerializer, WasteClassificationResponseSerializer
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View
from rest_framework.permissions import IsAuthenticated



class WasteClassificationView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        Handle waste classification requests
        """
        # Check if an image was uploaded
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_file = request.FILES['image']

        # Validate file type
        if not isinstance(image_file, InMemoryUploadedFile):
            return Response(
                {'error': 'Invalid file type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get confidence threshold from request or use default
        confidence_threshold = float(request.data.get('confidence_threshold', 1.5))

        # Make prediction
        result = waste_classifier.predict_image(image_file, confidence_threshold)

        # If prediction was successful, save to database
        if result['success']:
            classification = WasteClassification.objects.create(
                image=image_file,
                predicted_class=result['predicted_class'],
                confidence_score=result['confidence_score'],
                bin_score=result['bin_score'],
                product_type=result['product_type']
            )
            
            # Include the saved image URL in the response
            result['image_url'] = classification.image.url

            # Serialize and return the response
            serializer = WasteClassificationResponseSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If prediction failed, return the error response
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Retrieve classification history
        """
        classifications = WasteClassification.objects.all()
        serializer = WasteClassificationSerializer(classifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ServeWasteImageView(APIView):
    permission_classes = [IsAuthenticated]  # Si vous voulez l'authentification

    def get(self, request, filename):
        try:
            # Construire le chemin complet du fichier
            file_path = os.path.join(settings.MEDIA_ROOT, 'waste_classifications', filename)
            
            # Vérifier si le fichier existe
            if not os.path.exists(file_path):
                raise Http404("L'image demandée n'existe pas")
            
            # Vérifier que le chemin ne sort pas du dossier média
            if not os.path.abspath(file_path).startswith(os.path.abspath(settings.MEDIA_ROOT)):
                raise Http404("Accès non autorisé")
            
            # Servir le fichier
            response = FileResponse(open(file_path, 'rb'))
            return response
            
        except Exception as e:
            raise Http404(f"Erreur lors de l'accès à l'image: {str(e)}")