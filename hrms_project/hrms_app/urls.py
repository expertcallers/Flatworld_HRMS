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
    path('manager-dashboard', managerDashboard),

    # User Management
    path('add-new-user', addNewUser),
    path('add-new-designation', addNewDesi),
    path('viewusers', viewUsersHR),
    path('view-employee-profile/<int:id>/<str:on_id>', viewEmployeeProfile),

    # Team Management
    path('add-newteam', addNewTeam),
    path('departments', viewTeam),
    path('view-all-employees-oms/<str:name>', viewallOMS),

    # Leave
    path('ams-apply_leave', applyLeave),
    path('view-leave-escalation-mgr', viewEscalation),

    # Leave Management
    path('ams-apply_leave', applyLeave),
    path('view-initial-leave-request', initialLeaveRequest),
    path('approve-leave-rm1', approveLeaveRM1),
    path('view-final-leave-request', finalLeaveRequest),
    path('sl-proof', SLProofSubmit),
    path('apply-escalation', applyEscalation),
    path('leave-history', viewLeaveHistory),

    # Assets
    path('assets', assetsAssigning),
    path('edit-asset', assetsEdit),
    path('delete-asset', assetsDelete),

    # Attendance
    path('attendance', applyAttendace),
    path('week-attendance', weekAttendanceReport),

    # reimbursement
    path('reimbursement', Reimbursement),
    path('edit-reimbursement', editReimbursement),
    path('delete-reimbursement', deleteReimbursement),
    path('view-reimbursement', viewReimbursement),

    path('test', testFun),

]