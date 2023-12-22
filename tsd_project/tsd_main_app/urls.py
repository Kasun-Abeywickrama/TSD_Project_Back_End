from django.urls import path
from .web_app_views import AdminUserSigninView, PageListCreateView, PageRetrieveUpdateDeleteView

urlpatterns = [
    path('signin/', AdminUserSigninView.as_view(), name='register-admin-user'),
     path('page/', PageListCreateView.as_view(), name='yourmodel-list-create'),
    path('page/<int:pk>/',PageRetrieveUpdateDeleteView.as_view(), name='yourmodel-retrieve-update-delete'),
]


