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
from django.urls import path
from tsd_main_app.views import UserRegisterView, UserLoginView, QuizSendingView, QuizResultStoringView, QuizResultSendingView, PreviousQuizResultSendingView, UserPersonalDetailsSendingView, UserPersonalDetailsUpdateView, UserAuthUserDetailsSendingView, UserAuthUserDetailsUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),

    #URL of registering the user
    path('register/', UserRegisterView.as_view(), name='register-user'),
    
    #URL of user login
    path('login/', UserLoginView.as_view(), name='login-user'),

    #URL of sending questions and answers
    path('quiz_send/',QuizSendingView.as_view(), name='quiz-send'),

    #URL to store the quiz result and q and a data
    path('quiz_data_store/', QuizResultStoringView.as_view(), name='quiz-data-store'),

    #URL to view the quiz results
    path('view_quiz_result/', QuizResultSendingView.as_view(), name='view-quiz-result'),

    #URL to send the previous quiz results
    path('view_previous_quiz_results/', PreviousQuizResultSendingView.as_view(), name='view-previous-quiz-results'),

    #URL to send the user personal details
    path('send_user_personal_details/', UserPersonalDetailsSendingView.as_view(), name='send-user-personal-details'),

    #URL to update the user personal details
    path('update_user_personal_details/', UserPersonalDetailsUpdateView.as_view(), name='update-user-personal-details'),

    #Path to send user auth user details
    path('send_user_auth_user_details/', UserAuthUserDetailsSendingView.as_view(), name = 'send-user-auth-user-details'),

    #path to update user auth user details
    path('update_user_auth_user_details/', UserAuthUserDetailsUpdateView.as_view(), name='update-user-auth-user-details')

]
