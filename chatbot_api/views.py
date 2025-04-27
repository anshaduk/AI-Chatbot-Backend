from django.shortcuts import render
from rest_framework import status,viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from . models import Conversation,Message,KnowledgeDocument
from . serializers import (
    ConversationSerializer,
    MessageSerializer,
    ChatInputSerializer,
    KnowledgeDocumentSerializer
)
from .llm_service import ChatbotService


chatbot_service = ChatbotService()


class ChatView(APIView):
    def post(self,request):
        serializer = ChatInputSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data['message']
            conversation_id = serializer.validated_data.get('conversation_id','')

            if not conversation_id:
                conversation_id = chatbot_service.generate_conversation_id()

            chatbot_service.save_user_message(conversation_id,user_message)

            bot_response = chatbot_service.generate_response(conversation_id,user_message)

            chatbot_service.save_bot_response(conversation_id,bot_response)

            return Response({
                'conversation_id': conversation_id,
                'response': bot_response
            })
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer

    def retrieve(self, request, pk=None):
        try:
            conversation = Conversation.objects.get(conversation_id=pk)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {"error":"Conversation not found"},
                status=status.HTTP_404_NOT_FOUND
            )    
        

class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeDocument.objects.all().order_by('-created_at')
    serializer_class = KnowledgeDocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        title = serializer.validated_data['title']
        content = serializer.validated_data['content']

        document = serializer.save()

        success = chatbot_service.add_document_to_knowledge_base(title,content)

        return Response(
            {
                'id': document.id,
                'title': document.title,
                'added_to_knowledge_base': success
            },
            status=status.HTTP_201_CREATED
        )
