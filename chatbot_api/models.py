from django.db import models
import uuid


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-updated_at']


    def __str__(self):
        return f"Conversation {self.id}"
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    conversation = models.ForeignKey(Conversation,related_name='messages',on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['timestamp']


    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.content[:50]}..."
    

class KnowledgeDocument(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    embedding_stored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return self.title
    
