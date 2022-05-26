from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class ProfileSearch(admin.ModelAdmin):
    search_fields = ('emp_name', 'emp_id', "emp_desi", 'emp_department')
    list_display = ('emp_name', 'emp_id', 'emp_desi', 'emp_department', "emp_rm1", "emp_rm2", "emp_rm3",'agent_status')
    list_filter = ("agent_status",)

class LoginHistorySearch(admin.ModelAdmin):
    search_fields = ('profile', 'date')
    list_display = ('profile', 'id', 'date', 'login', 'logout','done')
    list_filter = ("date",)

class LeaveSearch(admin.ModelAdmin):
    search_fields = ('profile',)
    list_display = ('profile',"pl_balance","sl_balance")
class LeaveTableSearch(admin.ModelAdmin):
    search_fields = ('profile',)
    list_display = ('profile','applied_date','leave_type','start_date','end_date','no_days','tl_approval','manager_approval', 'escalation', 'status')
    list_filter = ('tl_approval','manager_approval', 'escalation', 'status')
class LeaveHistorySearch(admin.ModelAdmin):
    search_fields = ('profile','date')
    list_display = ('date','profile',"leave_type","transaction","no_days",'total')

class AttendanceResourse(resources.ModelResource):
  class Meta:
      model = AttendanceCalendar


class AttendanceSearch(ImportExportModelAdmin):
    search_fields = ('emp_name','emp_id',"att_actual")
    list_display = ('emp_name','emp_id',"date","att_actual")
    list_filter = ("date","att_actual")
    resource_class = AttendanceResourse

admin.site.register(AttendanceCalendar, AttendanceSearch)
admin.site.register(Profile, ProfileSearch)
admin.site.register(LoginHistory, LoginHistorySearch)
admin.site.register(EmployeeLeaveBalance, LeaveSearch)
admin.site.register(LeaveTable, LeaveTableSearch)
admin.site.register(AssetsDetails)
admin.site.register(Departments)
admin.site.register(Designation)
admin.site.register(leaveHistory, LeaveHistorySearch)