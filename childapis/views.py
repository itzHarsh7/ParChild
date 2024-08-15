from django.shortcuts import render
from parentapis.models import SearchHistory,NotAllowedSearches
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsChild
from childapis.utils import SafeSearchModel,search_youtube
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QuerySerializer

# Create your views here.
class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated, IsChild]

    def post(elf, request):
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            SearchHistory.objects.create(user=request.user,query=query)
            safe_search_result = SafeSearchModel(query)
            if safe_search_result == 'Not Allowed':
                NotAllowedSearches.objects.create(user=request.user, searches=query)
                return Response({'message':"This search query is not allowed according to YouTube's policy."},status=status.HTTP_200_OK)
            else:
                search_results = search_youtube(query, language='en')
                items = search_results.get('items', [])
                return Response({"message": "Search results processed and saved."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)