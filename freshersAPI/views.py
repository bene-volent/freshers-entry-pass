from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import EntryPass
from .serializers import EntryPassSerializer
from rest_framework import status
import csv
from django.shortcuts import redirect

def download(request: HttpRequest):
    """
    View to download the entry passes details as a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="passes.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Roll No', 'Branch', 'Year', 'Attended'])
    
    passes = EntryPass.objects.all()
    response_data = []
    for entry_pass in passes:
        response_data.append([entry_pass.name, entry_pass.roll_no, entry_pass.branch, entry_pass.year, entry_pass.attended])
    
    writer.writerows(response_data)
    
    return response

CACHE_TIMEOUT = 60*6  # 10 minutes

class EntryPassView(viewsets.ViewSet):
    """
    ViewSet for handling EntryPass operations.
    """
    
    def list(self, request: Request):
        """
        List all entry passes.
        """
        cache_key = 'entry_pass_list'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({'passes': cached_data})
        
        queryset = EntryPass.objects.all()
        serializer = EntryPassSerializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=CACHE_TIMEOUT)  # Cache for 15 minutes
        return Response({'passes': serializer.data})
    
    def create(self, request: Request):
        """
        Create a new entry pass.
        """
        serializer = EntryPassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete('entry_pass_list')  # Invalidate cache
            return Response({'pass': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request: Request, pk=None):
        """
        Retrieve an entry pass by its primary key.
        """
        cache_key = f'entry_pass_{pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({'pass': cached_data}, status=status.HTTP_200_OK)
        
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first())
            data = serializer.data
            data['branch'] = entry_pass.first().branch
            data['year'] = entry_pass.first().year
            cache.set(cache_key, data, timeout=CACHE_TIMEOUT)  # Cache for 15 minutes
            return Response({'pass': data}, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def retrieve_by_roll_no(self, request: Request, roll_no=None):
        """
        Retrieve an entry pass by roll number.
        """
        cache_key = f'entry_pass_roll_no_{roll_no}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({'pass': cached_data}, status=status.HTTP_200_OK)
        
        entry_pass = EntryPass.objects.filter(roll_no=roll_no)
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first())
            data = serializer.data
            data['branch'] = entry_pass.first().branch
            data['year'] = entry_pass.first().year
            cache.set(cache_key, data, timeout=CACHE_TIMEOUT)  # Cache for 15 minutes
            return Response({'pass': data}, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request: Request, pk=None):
        """
        Update an entry pass by its primary key.
        """
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first(), data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'entry_pass_{pk}')  # Invalidate cache
                cache.delete('entry_pass_list')  # Invalidate cache
                return Response({'updatedFields': serializer.data})
            
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request: Request, pk=None):
        """
        Delete an entry pass by its primary key.
        """
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        if entry_pass.exists():
            entry_pass.delete()
            cache.delete(f'entry_pass_{pk}')  # Invalidate cache
            cache.delete('entry_pass_list')  # Invalidate cache
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def partial_update(self, request: Request, pk=None):
        """
        Partially update an entry pass by its primary key.
        """
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first(), data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'entry_pass_{pk}')  # Invalidate cache
                cache.delete('entry_pass_list')  # Invalidate cache
                return Response({'updatedFields': serializer.data})
            
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_404_NOT_FOUND)

def redirect_to_passes(request: HttpRequest):
    """
    Redirect to the passes list.
    """
    return redirect('/api/passes', status=302)

@api_view(['PATCH'])
def mark_attendance(request: Request):
    """
    Mark attendance for an entry pass.
    """
    pass_id = request.data.get('pass_id')
    
    if not pass_id:
        return Response({'error': 'pass_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        entry_pass = EntryPass.objects.get(pass_id=pass_id)
    except EntryPass.DoesNotExist:
        return Response({'error': 'EntryPass not found'}, status=status.HTTP_404_NOT_FOUND)
    
    entry_pass.attended = True
    entry_pass.save()
    
    # Invalidate cache
    cache.delete(f'entry_pass_{pass_id}')
    cache.delete('entry_pass_list')
    
    return Response({'updated': EntryPassSerializer(entry_pass).data}, status=status.HTTP_200_OK)