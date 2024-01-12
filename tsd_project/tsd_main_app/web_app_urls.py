from django.urls import path
from .web_app_views import LogoutView, PageListCreateView, PageRetrieveUpdateDeleteView, RegisterView, RoleListCreateView, SigninView, QuestionCreatingView, QuestionSendingView, QuestionUpdatingView, QuestionDeleteView, QuestionSelectingView, SetAppointment, ResultsListCreateView, ResultsRetrieveUpdateDeleteView


urlpatterns = [
    path('set-appointment/<int:pk>/', SetAppointment.as_view(), name='set-appointment-detail'),
    path('quiz-result/<int:pk>/', ResultsRetrieveUpdateDeleteView.as_view(), name='result-retrieve-update-delete'),
    path('result-list/', ResultsListCreateView.as_view(), name='result-list'),
    path('role/', RoleListCreateView.as_view(), name='role-list-create'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('signin/', SigninView.as_view(), name='register-admin-user'),
    path('page/', PageListCreateView.as_view(), name='page-list-create'),
    path('page/<int:pk>/',PageRetrieveUpdateDeleteView.as_view(), name='page-retrieve-update-delete'),
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('create_question/', QuestionCreatingView.as_view(), name='create-question'),
    path('send_questions/', QuestionSendingView.as_view(), name='send-questions'),
    path('update_question/', QuestionUpdatingView.as_view(), name='update-question'),
    path('delete_question/', QuestionDeleteView.as_view(), name='delete-question'),
    path('select_question/', QuestionSelectingView.as_view(), name='select_question'),

]


