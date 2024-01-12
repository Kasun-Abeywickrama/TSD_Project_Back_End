"""
URL configuration for tsd_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tsd_main_app.mobile_app_views import SendCounselorDetailsView, PatientRegisterView, PatientLoginView, QuizSendingView, QuizResultStoringView, QuizResultSendingView, PreviousQuizResultSendingView, PatientPersonalDetailsSendingView, PatientPersonalDetailsUpdateView, UserAuthUserDetailsSendingView, UserAuthUserDetailsUpdateView, MakeAppointmentView, checkOngoingAppointmentView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/wa/',include('tsd_main_app.urls')),

    #URL of registering the patient
    path('register/', PatientRegisterView.as_view(), name='register-patient'),
    
    #URL of patient login
    path('login/', PatientLoginView.as_view(), name='login-patient'),

    #URL of sending questions and answers
    path('quiz_send/',QuizSendingView.as_view(), name='quiz-send'),

    #URL to store the quiz result and q and a data
    path('quiz_data_store/', QuizResultStoringView.as_view(), name='quiz-data-store'),

    #URL to view the quiz results
    path('view_quiz_result/', QuizResultSendingView.as_view(), name='view-quiz-result'),

    #URL to send the previous quiz results
    path('view_previous_quiz_results/', PreviousQuizResultSendingView.as_view(), name='view-previous-quiz-results'),

    #URL to send the patient personal details
    path('send_patient_personal_details/', PatientPersonalDetailsSendingView.as_view(), name='send-patient-personal-details'),

    #URL to update the patient personal details
    path('update_patient_personal_details/', PatientPersonalDetailsUpdateView.as_view(), name='update-patient-personal-details'),

    #Path to send user auth user details
    path('send_user_auth_user_details/', UserAuthUserDetailsSendingView.as_view(), name = 'send-user-auth-user-details'),

    #path to update user auth user details
    path('update_user_auth_user_details/', UserAuthUserDetailsUpdateView.as_view(), name='update-user-auth-user-details'),

    #path to send the counselor details 
    path('send_counselor_details/', SendCounselorDetailsView.as_view(), name = 'send-counselor-details'),

    #path to make the appointment 
    path('make_appointment/', MakeAppointmentView.as_view(), name = 'make-appointment'),

    #path to check ongoing appointment 
    path('check_ongoing_appointment/', checkOngoingAppointmentView.as_view(), name = 'check-ongoing-appoointment'),

]
