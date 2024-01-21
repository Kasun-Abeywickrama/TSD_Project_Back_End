from django.urls import path
from .mobile_app_views import AppointmentListSendingView, MakeIsPatientViewedTrueView, SendCounselorDetailsView, PatientRegisterView, PatientLoginView, QuizSendingView, QuizResultStoringView, QuizResultSendingView, PreviousQuizResultSendingView, PatientPersonalDetailsSendingView, PatientPersonalDetailsUpdateView, PatientAuthUserDetailsSendingView, PatientAuthUserDetailsUpdateView, MakeAppointmentView, SendNotificationAmountView, checkOngoingAppointmentView


urlpatterns = [
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

    #Path to send patient auth user details
    path('send_patient_auth_user_details/', PatientAuthUserDetailsSendingView.as_view(), name = 'send-patient-auth-user-details'),

    #path to update patient auth user details
    path('update_patient_auth_user_details/', PatientAuthUserDetailsUpdateView.as_view(), name='update-patient-auth-user-details'),

    #path to send the counselor details 
    path('send_counselor_details/', SendCounselorDetailsView.as_view(), name = 'send-counselor-details'),

    #path to make the appointment 
    path('make_appointment/', MakeAppointmentView.as_view(), name = 'make-appointment'),

    #path to check ongoing appointment 
    path('check_ongoing_appointment/', checkOngoingAppointmentView.as_view(), name = 'check-ongoing-appoointment'),

    #path to send the appointment list
    path('send_appointment_list/', AppointmentListSendingView.as_view(), name='send-appointment-list'),

    #path to make is_patient_viewed true
    path('make_is_patient_viewed_true/', MakeIsPatientViewedTrueView.as_view(), name='make-is-patient-viewed-true'),

    #path to send the notification amount
    path('send_notification_amount/', SendNotificationAmountView.as_view(), name='send-notification-amount'),
]