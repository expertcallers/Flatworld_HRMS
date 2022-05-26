from django.urls import path
from .views import *


urlpatterns = [
    path('', loginPage),
    path('login', loginAndRedirect),
    path('logout', loginPage),
    path('start-login', startLogin),
    path('stop-login', stopLogin),
    path('get-emp', getEmp),
    path('settings', Settings),
    path('upload-image', uploadImageToDB),
    path('dashboard', DashboardRedirect),
    path('change-password', change_password),

    # Dashboards
    path('hr-dashboard', hrDashboard),
    path('agent-dashboard', agentDashBoard),

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
    path('edit-asset', assetsEdit),
    path('delete-asset', assetsDelete),

    # Attendance
    path('attendance', applyAttendace),

]