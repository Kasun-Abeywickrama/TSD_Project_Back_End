from django.urls import path
from .web_app_views import AccountRetrieveUpdateDeleteView, AccountsView, AppointmentListView, LogoutView, PageListCreateView, PageRetrieveUpdateDeleteView, PrivateQuestionListCreateView, PrivateQuestionsRetrieveUpdateDestroyView, QuestionListCreateView, RegisterView, RoleListCreateView, RoleRetrieveUpdateDeleteView, SigninView, QuestionCreatingView, QuestionSendingView, QuestionUpdatingView, QuestionDeleteView, QuestionSelectingView, SetAppointment, ResultsListCreateView, ResultsRetrieveUpdateDeleteView, get_csrf_token, get_current_user, get_user_completed_appointments, get_user_pending_appointments, get_user_role_pages, reset_password, send_otp, update_current_user, user_appointment_details, user_appointments_count, user_private_questions_count
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('user_private_questions_count/', user_private_questions_count,name='user-private-questions-count'),
    path('user_appointments_count/',user_appointments_count,name='user-appointments-count'),
    path('private-question-retrieve-update-delete/<int:pk>/', PrivateQuestionsRetrieveUpdateDestroyView.as_view(), name='private-question-retrieve-update-delete'),
    path('private_question/', PrivateQuestionListCreateView.as_view(), name='private-question'),
    path('get_update_delete_user_role/<int:pk>/', RoleRetrieveUpdateDeleteView.as_view(), name='update_role'),
    path('get_role_pages/<int:pk>/', get_user_role_pages, name='get-role-pages'),
    path('update_current_user/',update_current_user,name='update-user-account-details'),
    path('get_current_user/', get_current_user, name='get-current-user'),
    path('question-list/',QuestionListCreateView.as_view(), name='question-list-create'),
    path('get_user_account_details/<int:pk>/', AccountRetrieveUpdateDeleteView.as_view(), name='get-user-account-details'),
    path('get_all_accounts/',AccountsView.as_view(), name='get-all-accounts'),
    path('retrieve_update_delete_user_account/<int:pk>/', AccountRetrieveUpdateDeleteView.as_view(), name='update-user-account-details'),
    path('user_appointment_details/<int:pk>/',user_appointment_details, name='user-appointment-details'),
    path('user_pending_appointments/', get_user_pending_appointments, name='user-pending-appointments'),
    path('user_completed_appointments/', get_user_completed_appointments, name='user-completed-appointments'),
    path('complete-appointment/<int:pk>/', SetAppointment.as_view(), name='complete-appointment'),
    path('appointment-list/', AppointmentListView.as_view(), name='appointment-list'),
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
    path('role/<int:pk>/', RoleRetrieveUpdateDeleteView.as_view(), name='role-retrieve-update-delete'),
    path('create_question/', QuestionCreatingView.as_view(), name='create-question'),
    path('send_questions/', QuestionSendingView.as_view(), name='send-questions'),
    path('update_question/', QuestionUpdatingView.as_view(), name='update-question'),
    path('delete_question/', QuestionDeleteView.as_view(), name='delete-question'),
    path('select_question/', QuestionSelectingView.as_view(), name='select_question'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send_otp/', send_otp, name='send-otp'),
    path('reset_password/', reset_password, name='reset-password'),
    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),

]


