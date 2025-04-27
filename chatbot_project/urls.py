from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from chatbot_api.views import ChatView,ConversationViewSet,KnowledgeDocumentViewSet

router = DefaultRouter()
router.register(r'conversations',ConversationViewSet)
router.register(r'documents',KnowledgeDocumentViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/chat/",ChatView.as_view(),name="chat"),
    path("api/",include(router.urls)),
]
