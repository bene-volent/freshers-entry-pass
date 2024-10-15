from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import EntryPass
from .serializers import EntryPassSerializer
from rest_framework import status
from django.shortcuts import redirect

class EntryPassView(viewsets.ViewSet):
    
    # API to list all the passes
    def list(self,request:Request):
        queryset = EntryPass.objects.all()
        serializer = EntryPassSerializer(queryset,many=True)
        return Response({'passes':serializer.data})
    
    # API to create a new pass
    def create(self,request:Request):
        
        serializer = EntryPassSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'pass':serializer.data},status=status.HTTP_201_CREATED)
        
        return Response({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self,request:Request,pk=None):
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first())
            
            data = serializer.data
            data['branch'] = entry_pass.first().branch
            data['year'] = entry_pass.first().year
            return Response({'pass': data}, status=status.HTTP_200_OK)
            
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def retrieve_by_roll_no(self,request:Request,roll_no=None):
        entry_pass = EntryPass.objects.filter(roll_no=roll_no)
        
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first())
            
            data = serializer.data
            data['branch'] = entry_pass.first().branch
            data['year'] = entry_pass.first().year
            return Response({'pass': data}, status=status.HTTP_200_OK)
            
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request:Request, pk=None):
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first(), data=request.data) 
            
            if serializer.is_valid():
                serializer.save()
                return Response({'updatedFields': serializer.data})
            
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    
    def destroy(self,request:Request,pk=None):
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        
        if entry_pass.exists():
            entry_pass.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def partial_update(self, request: Request, pk=None):
        entry_pass = EntryPass.objects.filter(pass_id=pk)
        
        if entry_pass.exists():
            serializer = EntryPassSerializer(entry_pass.first(), data=request.data, partial=True)  
            
            if serializer.is_valid():
                serializer.save()
                return Response({'updatedFields': serializer.data})
            
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    

def redirect_to_passes(request: HttpRequest):
    return redirect('/api/passes',status=302)

@api_view(['PATCH'])
def mark_attendance(request: Request):
    pass_id = request.data.get('pass_id')
    
    if not pass_id:
        return Response({'error': 'pass_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        entry_pass = EntryPass.objects.get(pass_id=pass_id)
    except EntryPass.DoesNotExist:
        return Response({'error': 'EntryPass not found'}, status=status.HTTP_404_NOT_FOUND)
    
    entry_pass.attended = True
    entry_pass.save()
    
    return Response({'updated': EntryPassSerializer(entry_pass).data}, status=status.HTTP_200_OK)


