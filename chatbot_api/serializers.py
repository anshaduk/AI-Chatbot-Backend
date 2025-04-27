from rest_framework import serializers
from . models import Conversation,Message,KnowledgeDocument


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id','content','is_user','timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True,read_only=True)


    class Meta:
        model = Conversation
        fields = ['id','created_at','updated_at','messages']


class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    conversation_id = serializers.UUIDField(required=False,allow_null=True)


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeDocument
        fields = ['id','title','content','embedding_stored','created_at','updated_at']
        read_only_fields = ['embedding_stored']