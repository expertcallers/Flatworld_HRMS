from datetime import date

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=100)
    emp_name = models.CharField(max_length=200)
    emp_email = models.EmailField(null=True, blank=True)
    emp_desi = models.CharField(max_length=200, null=True, blank=True)
    emp_rm1 = models.CharField(max_length=200, null=True, blank=True)
    emp_rm1_id = models.CharField(max_length=10, null=True, blank=True)
    emp_rm2 = models.CharField(max_length=200, null=True, blank=True)
    emp_rm2_id = models.CharField(max_length=10, null=True, blank=True)
    emp_rm3 = models.CharField(max_length=200, null=True, blank=True)
    emp_rm3_id = models.CharField(max_length=10, null=True, blank=True)
    emp_department = models.CharField(max_length=200, null=True, blank=True)
    emp_department_id = models.CharField(max_length=10, null=True, blank=True)
    pc = models.BooleanField(default=False)
    img = models.ImageField(upload_to='users/', default="users/default.png")
    doj = models.DateField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    on_id = models.IntegerField(null=True, blank=True)
    agent_status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return self.emp_name


class Departments(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=100)
    om = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.CharField(max_length=200, default="CC Team")


#
# class OnboardingnewHRC(models.Model):
#     unique_id = models.CharField(max_length=150, null=True, blank=True)
#     hr_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hrname', null=True, blank=True)
#     submit_date = models.DateTimeField(default=datetime.now())
#     emp_id = models.CharField(max_length=20, null=True, blank=True)
#     emp_name = models.CharField(max_length=200, null=True, blank=True)
#     emp_dob = models.DateField(null=True, blank=True)
#     emp_desig = models.CharField(max_length=150, null=True, blank=True)
#     emp_department = models.CharField(max_length=50, null=True, blank=True)
#     emp_pan = models.CharField(max_length=50, null=True, blank=True)
#     emp_aadhar = models.CharField(max_length=50, null=True, blank=True)
#     emp_father_name = models.CharField(max_length=50, null=True, blank=True)
#     emp_marital_status = models.CharField(max_length=50, null=True, blank=True)
#     emp_email = models.EmailField(null=True, blank=True)
#     emp_phone = models.CharField(max_length=50, null=True, blank=True)
#     emp_alt_phone = models.CharField(max_length=50, null=True, blank=True)
#     emp_present_address = models.CharField(max_length=500, null=True, blank=True)
#     emp_permanent_address = models.CharField(max_length=500, null=True, blank=True)
#     emp_blood = models.CharField(max_length=5, null=True, blank=True)
#     emp_emergency_person = models.CharField(max_length=50, null=True, blank=True)
#     emp_emergency_number = models.CharField(max_length=50, null=True, blank=True)
#     emp_emergency_address = models.CharField(max_length=500, null=True, blank=True)
#     emp_emergency_person_two = models.CharField(max_length=50, null=True, blank=True)
#     emp_emergency_number_two = models.CharField(max_length=50, null=True, blank=True)
#     emp_emergency_address_two = models.CharField(max_length=500, null=True, blank=True)
#     emp_edu_qualification = models.CharField(max_length=50, null=True, blank=True)
#     emp_quali_other = models.CharField(null=True, max_length=100, blank=True)
#     emp_edu_course = models.CharField(null=True, max_length=50, blank=True)
#     emp_edu_institute = models.CharField(max_length=200, null=True, blank=True)
#     emp_pre_exp = models.IntegerField(null=True, blank=True, default=0)
#     emp_pre_industry = models.CharField(max_length=50, null=True, blank=True)
#     emp_pre_org_name = models.CharField(max_length=150, null=True, blank=True)
#     emp_pre_desg = models.CharField(max_length=50, null=True, blank=True)
#     emp_pre_period_of_employment_frm = models.DateField(null=True, blank=True)
#     emp_pre_period_of_employment_to = models.DateField(null=True, blank=True)
#     emp_pre_exp_two = models.IntegerField(null=True, blank=True, default=0)
#     emp_pre_industry_two = models.CharField(max_length=50, null=True, blank=True)
#     emp_pre_org_name_two = models.CharField(max_length=150, null=True, blank=True)
#     emp_pre_desg_two = models.CharField(max_length=50, null=True, blank=True)
#     emp_pre_period_of_employment_frm_two = models.DateField(null=True, blank=True)
#     emp_pre_period_of_employment_to_two = models.DateField(null=True, blank=True)
#     emp_pre_exp_three = models.IntegerField(null=True, blank=True, default=0)
#     emp_pre_industry_three = models.CharField(max_length=50, null=True, blank=True)
#     emp_pre_org_name_three = models.CharField(max_length=150, null=True, blank=True)
#     emp_pre_desg_three = models.CharField(max_length=50, null=True, blank=True)
#     emp_pre_period_of_employment_frm_three = models.DateField(null=True, blank=True)
#     emp_pre_period_of_employment_to_three = models.DateField(null=True, blank=True)
#     emp_bank_holder_name = models.CharField(max_length=50, null=True, blank=True)
#     emp_bank_name = models.CharField(max_length=50, null=True, blank=True)
#     emp_bank_acco_no = models.CharField(max_length=50, null=True, blank=True)
#     emp_bank_ifsc = models.CharField(max_length=11, null=True, blank=True)
#     have_system = models.CharField(null=True, max_length=10, blank=True)
#     require_system = models.CharField(null=True, max_length=10, blank=True)
#     wifi_broadband = models.CharField(null=True, max_length=10, blank=True)
#     emp_upload_aadhar = models.ImageField(upload_to='Aadhar/', null=True, blank=True)
#     emp_upload_aadhar_back = models.ImageField(upload_to='Aadhar/', null=True, blank=True)
#     emp_upload_pan = models.ImageField(upload_to='Pan/', null=True, blank=True)
#     emp_upload_id = models.ImageField(upload_to='Id/', null=True, blank=True)
#     emp_upload_id_back = models.ImageField(upload_to='Id/', null=True, blank=True)
#     emp_upload_edu_sslc = models.ImageField(upload_to='Certificate/', null=True, blank=True)
#     emp_upload_edu_twelveth = models.ImageField(upload_to='Certificate/', null=True, blank=True)
#     emp_upload_edu_gradu = models.ImageField(upload_to='Certificate/', null=True, blank=True)
#     emp_upload_experience = models.ImageField(upload_to='Experience/', null=True, blank=True)
#     emp_upload_experience_two = models.ImageField(upload_to='Experience/', null=True, blank=True)
#     emp_upload_experience_three = models.ImageField(upload_to='Experience/', null=True, blank=True)
#     emp_upload_bank = models.ImageField(upload_to='Passbook/', null=True, blank=True)
#     esic = models.CharField(max_length=20, null=True, blank=True)
#     pf = models.CharField(max_length=20, null=True, blank=True)
#     tds = models.CharField(max_length=20, null=True, blank=True)
#     pt = models.CharField(max_length=20, null=True, blank=True)
#     user_created = models.BooleanField(default=False)


class LoginHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    date = models.DateField(null=True, blank=True)
    login = models.DateTimeField(null=True, blank=True)
    logout = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)


class LeaveTable(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    leave_type = models.CharField(max_length=50, null=True)
    applied_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    no_days = models.IntegerField()
    agent_reason = models.TextField(null=True)
    tl_approval = models.BooleanField(default=False)
    tl_status = models.CharField(max_length=50, null=True, blank=True)
    tl_reason = models.TextField(null=True)
    status = models.CharField(max_length=50, null=True)
    manager_approval = models.BooleanField(default=False)
    manager_reason = models.TextField(null=True)
    manager_status = models.CharField(max_length=50, null=True, blank=True)
    escalation = models.BooleanField(default=False)
    escalation_reason = models.TextField(null=True)
    proof = models.FileField(null=True, blank=True, upload_to='SL_Proof/')


class leaveHistory(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    date = models.DateField()
    leave_type = models.CharField(max_length=30)
    transaction = models.CharField(max_length=300)
    no_days = models.FloatField()
    total = models.FloatField(null=True, blank=True)


class EmployeeLeaveBalance(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    pl_balance = models.FloatField()
    sl_balance = models.FloatField()


class AssetsDetails(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    added_on = models.DateTimeField()
    added_by = models.CharField(max_length=300)
    added_by_id = models.CharField(max_length=30)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    type = models.CharField(max_length=100)
    given_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    details = models.TextField()


class AttendanceCalendar(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    team = models.CharField(max_length=300)
    date = models.DateField()
    emp_name = models.CharField(max_length=300)
    emp_id = models.CharField(max_length=50, null=True)
    emp_desi = models.CharField(max_length=100, null=True)
    att_actual = models.CharField(max_length=50, null=True)
    approved_on = models.DateTimeField(null=True)
    appoved_by = models.CharField(max_length=300, null=True)
    rm1 = models.CharField(max_length=200, null=True)
    rm2 = models.CharField(max_length=200, null=True)
    rm3 = models.CharField(max_length=200, null=True)
    rm1_id = models.CharField(max_length=30, null=True)
    rm2_id = models.CharField(max_length=30, null=True)
    rm3_id = models.CharField(max_length=30, null=True)
    team_id = models.IntegerField(null=True, blank=True)


class ReimbursementTickets(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, blank=True)
    submit_date = models.DateField(default=date.today(), blank=True)
    date_for = models.DateField(blank=True)
    type = models.CharField(max_length=100, blank=True)
    amount = models.CharField(max_length=100, blank=True)
    bill = models.FileField(upload_to='Reimbursement Bills/', blank=True)
    details = models.TextField(blank=True)
    approved_by = models.CharField(max_length=150, null=True, blank=True)
    approved_by_id = models.CharField(max_length=50, null=True, blank=True)
    approved_on = models.DateField(blank=True, null=True)
    approval_comments = models.TextField(blank=True, null=True)
    respond = models.BooleanField(default=False)
    status = models.CharField(max_length=150, default='Pending')
