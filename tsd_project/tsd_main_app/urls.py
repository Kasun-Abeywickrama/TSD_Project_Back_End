from django.urls import path
from .web_app_views import LogoutView, PageListCreateView, PageRetrieveUpdateDeleteView, RegisterView, RoleListCreateView, SigninView


urlpatterns = [
    path('role/', RoleListCreateView.as_view(), name='role-list-create'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('signin/', SigninView.as_view(), name='register-admin-user'),
    path('page/', PageListCreateView.as_view(), name='page-list-create'),
    path('page/<int:pk>/',PageRetrieveUpdateDeleteView.as_view(), name='page-retrieve-update-delete'),
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),

]


