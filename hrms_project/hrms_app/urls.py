from django.urls import path
from .views import *


urlpatterns = [
    path('', loginPage),
    path('login', loginAndRedirect),
    path('logout', loginPage),
    path('hr-dashboard', hrDashboard),
    path('start-login', startLogin),
    path('stop-login', stopLogin),
    path('get-emp', getEmp),
    path('settings', Settings),
    path('upload-image', uploadImageToDB),
    path('dashboard', DashboardRedirect),
    path('change-password', change_password),

    # User Management
    path('add-new-user', addNewUser),
    path('add-new-designation', addNewDesi),
    path('viewusers', viewUsersHR),

    # Team Management
    path('add-newteam', addNewTeam),
    path('departments', viewTeam),

    # Leave
    path('ams-apply_leave', applyLeave),

    # Assets
    path('assets', assetsAssigning),

    # Attendance
    path('attendance', applyAttendace),

]