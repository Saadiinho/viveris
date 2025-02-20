from django.urls import path
from .views import invite_friend

urlpatterns = [
    # POST: /api/invites/invite/
    path('invite/', invite_friend, name='invite_friend'),
]
