import calendar
import csv
import json
import os
from datetime import timedelta, datetime

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from monthdelta import monthdelta

from .models import *

hr_list = ['HR']
agent_list = ['Agent']
manager_list = ['Manager']


# Create your views here.
def loginPage(request):  # Test1 Test2
    logout(request)
    form = AuthenticationForm()
    data = {'form': form}
    return render(request, 'login.html', data)


def loginAndRedirect(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if request.user.profile.agent_status == "Active":
                if request.user.profile.pc == False:
                    return redirect('/change-password')
                else:
                    return redirect('/dashboard')
            else:
                messages.info(request, 'You are Inactive. Please contact HR.')
                return redirect("/")
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect("/")
    else:
        return redirect("/")


@login_required
def change_password(request):  # Test1 Test2
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            user = request.user.profile
            user.pc = True
            user.save()
            logout(request)
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'change-password.html', {'form': form})


@login_required
def DashboardRedirect(request):
    emp_desi = request.user.profile.emp_desi
    if emp_desi in hr_list:
        return redirect("/hr-dashboard")
    elif emp_desi in agent_list:
        return redirect("/agent-dashboard")
    elif emp_desi in manager_list:
        return redirect("/manager-dashboard")
    else:
        messages.info(request, 'Invalid Request.')
        return redirect("/")


@login_required
def hrDashboard(request):
    profile = request.user.profile
    # Check in start
    login = False
    login_id = None
    try:
        login = LoginHistory.objects.filter(profile=profile, done=False).order_by('id')[:1]
        if login:
            for i in login:
                login_id = i.id
                login = str(i.login)
        else:
            login = False
            login_id = None
    except LoginHistory.DoesNotExist:
        pass
    try:
        login = LoginHistory.objects.get(profile=profile, date=date.today(), done=True)
        login_id = datetime.strptime(str(login.logout - login.login), "%H:%M:%S.%f")
        login_id = (login_id).strftime("%H:%M:%S")
        login = True
    except LoginHistory.DoesNotExist:
        pass
    # Check in End
    # Birthday Start
    birthdays = []
    for i in Profile.objects.all():
        day = date.today().day
        month = date.today().month
        try:
            if day == i.dob.day and month == i.dob.month:
                birthdays.append(i)
        except:
            pass
    # Birthday End

    new_joins = Profile.objects.all().order_by('-id')[:5]

    # Attendance Month view Start
    month_days = []
    todays_date = date.today()
    year = todays_date.year
    month = todays_date.month
    a, num_days = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    delta = timedelta(days=1)
    while start_date <= end_date:
        month_days.append(start_date.strftime("%Y-%m-%d"))
        start_date += delta
    month_cal = []
    for i in month_days:
        dict = {}
        try:
            st = AttendanceCalendar.objects.get(Q(date=i), Q(emp_id=profile.emp_id)).att_actual
        except AttendanceCalendar.DoesNotExist:
            st = 'Unmarked'
        dict['dt'] = i
        dict['st'] = st
        month_cal.append(dict)
    # Attendance Month view End

    teams = Departments.objects.all()
    data = {'login': login, 'team': teams, 'login_id': login_id, 'birthdays': birthdays, 'new_joins': new_joins,
            'month_cal': month_cal}
    return render(request, 'hr/hr_dashboard.html', data)


@login_required
def agentDashBoard(request):  # Test1 Test2
    if request.user.profile.emp_desi in agent_list:
        profile = request.user.profile
        # Check in start
        login = False
        login_id = None
        try:
            login = LoginHistory.objects.filter(profile=profile, done=False).order_by('id')[:1]
            if login:
                for i in login:
                    login_id = i.id
                    login = str(i.login)
            else:
                login = False
                login_id = None
        except LoginHistory.DoesNotExist:
            pass
        try:
            login = LoginHistory.objects.get(profile=profile, date=date.today(), done=True)
            login_id = datetime.strptime(str(login.logout - login.login), "%H:%M:%S.%f")
            login_id = (login_id).strftime("%H:%M:%S")
            login = True
        except LoginHistory.DoesNotExist:
            pass
        # Check in End
        emp_id = request.user.profile.emp_id
        profile = request.user.profile
        emp = Profile.objects.get(emp_id=emp_id)
        # Leave status
        leave_hist = LeaveTable.objects.filter(Q(profile=profile), Q(leave_type__in=['SL', 'PL', 'ML'])).order_by(
            '-id')[:5]
        # Month view
        month_days = []
        todays_date = date.today()
        year = todays_date.year
        month = todays_date.month
        a, num_days = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)
        delta = timedelta(days=1)
        while start_date <= end_date:
            month_days.append(start_date.strftime("%Y-%m-%d"))
            start_date += delta
        month_cal = []
        for i in month_days:
            dict = {}
            try:
                st = AttendanceCalendar.objects.get(Q(date=i), Q(emp_id=emp_id)).att_actual
            except AttendanceCalendar.DoesNotExist:
                st = 'Unmarked'
            dict['dt'] = i
            dict['st'] = st
            month_cal.append(dict)
        data = {'login': login, 'login_id': login_id, 'emp': emp, 'leave_hist': leave_hist, 'month_cal': month_cal}
        return render(request, 'agent/agent-dashboard.html', data)
    else:
        messages.error(request, 'Unauthorized access. You have been Logged Our !')
        return redirect('')


@login_required
def managerDashboard(request):  # Test1 Test2
    profile = request.user.profile
    # Check in start
    login = False
    login_id = None
    try:
        login = LoginHistory.objects.filter(profile=profile, done=False).order_by('id')[:1]
        if login:
            for i in login:
                login_id = i.id
                login = str(i.login)
        else:
            login = False
            login_id = None
    except LoginHistory.DoesNotExist:
        pass
    try:
        login = LoginHistory.objects.get(profile=profile, date=date.today(), done=True)
        login_id = datetime.strptime(str(login.logout - login.login), "%H:%M:%S.%f")
        login_id = (login_id).strftime("%H:%M:%S")
        login = True
    except LoginHistory.DoesNotExist:
        pass
    # Check in End

    mgr_name = request.user.profile.emp_name
    emp_id = request.user.profile.emp_id

    emp = Profile.objects.get(emp_id=emp_id)
    # Leave Requests
    profilelist = []
    myprof = Profile.objects.filter(Q(emp_rm3_id=emp_id))
    for i in myprof:
        profilelist.append(i)
    ini_req_count = LeaveTable.objects.filter(profile__in=profilelist, tl_approval=False,
                                              manager_approval=False).count()

    final_req_count = LeaveTable.objects.filter(profile__in=profilelist, tl_approval=True,
                                                manager_approval=False).count()
    # Leave Escalation Count
    leave_esc_count = LeaveTable.objects.filter(profile__in=profilelist, manager_approval=False,
                                                escalation=True).count()

    # Month view
    month_days = []
    todays_date = date.today()
    year = todays_date.year
    month = todays_date.month
    a, num_days = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    delta = timedelta(days=1)
    while start_date <= end_date:
        month_days.append(start_date.strftime("%Y-%m-%d"))
        start_date += delta
    month_cal = []
    for i in month_days:
        dict = {}
        try:
            st = AttendanceCalendar.objects.get(Q(date=i), Q(emp_id=emp_id)).att_actual
        except AttendanceCalendar.DoesNotExist:
            st = 'Unmarked'
        dict['dt'] = i
        dict['st'] = st
        month_cal.append(dict)

    # All Employees
    all_emps = Profile.objects.filter(Q(agent_status='Active'),
                                      Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    all_emps_under = []
    for i in all_emps:
        if i not in all_emps_under:
            all_emps_under.append(i)
            under = Profile.objects.filter(Q(agent_status='Active'),
                                           Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
            for j in under:
                if j not in all_emps_under:
                    all_emps_under.append(j)

    # count of all employees
    count_all_emps = len(all_emps_under)

    # TLS
    all_tls_under = []
    for i in all_emps_under:
        if i not in all_tls_under:
            if i.emp_desi == 'Team Leader':
                all_tls_under.append(i)
    # TLS Count
    all_tls_count = len(all_tls_under)
    # AMS
    all_ams_under = []
    for i in all_emps_under:
        if i not in all_ams_under:
            if i.emp_desi == 'Assistant Manager':
                all_ams_under.append(i)

    # AMS Count
    all_ams_count = len(all_ams_under)

    profiles = Profile.objects.filter(Q(emp_rm1_id=emp_id) | Q(emp_rm3_id=emp_id) | Q(emp_rm3_id=emp_id))
    reimbursement = ReimbursementTickets.objects.filter(profile__in=profiles, respond=False).count()

    data = {'emp': emp, 'count_all_emps': count_all_emps, 'all_tls': all_tls_under, 'all_tls_count': all_tls_count,
            'all_ams': all_ams_under, 'all_ams_count': all_ams_count, 'final_req_count': final_req_count,
            'ini_req_count': ini_req_count, 'leave_esc_count': leave_esc_count, 'all_emp': all_emps_under,
            'month_cal': month_cal, 'login': login, 'login_id': login_id, 'reimbursement': reimbursement
            }
    return render(request, 'manager/manager-dashboard.html', data)


@login_required
def startLogin(request):
    if request.method == "POST":
        emp_id = request.POST['emp_id']
        profile = Profile.objects.get(emp_id=emp_id)
        try:
            LoginHistory.objects.get(profile=profile, date=date.today())
            messages.info(request, "Your had already Logged in and then Logged Out for Today! Can't Login again.")
        except LoginHistory.DoesNotExist:
            LoginHistory.objects.create(
                profile=profile, date=date.today(), login=datetime.now()
            )
        return redirect('/hr-dashboard')
    else:
        messages.info(request, 'Invalid Request')
        return redirect("/")


@login_required
def stopLogin(request):
    if request.method == "POST":
        id = request.POST['id']
        login = LoginHistory.objects.get(id=id)
        login.done = True
        login.logout = datetime.now()
        login.save()
        return redirect('/dashboard')
    else:
        messages.info(request, 'Invalid Request')
        return redirect("/")


@login_required
def getEmp(request):
    emp_id = request.POST['emp_id']
    profile = Profile.objects.get(emp_id=emp_id)
    prof_dict = {}
    prof_dict['emp_name'] = profile.emp_name
    prof_dict['emp_id'] = profile.emp_id
    prof_dict['emp_desi'] = profile.emp_desi
    prof_dict['emp_department'] = profile.emp_department
    prof_dict['img'] = str(profile.img)
    prof_dict['dob'] = str(profile.dob)
    prof_dict['doj'] = str(profile.doj)
    return HttpResponse(json.dumps(prof_dict))


@login_required
def applyLeave(request):  # Test1
    if request.method == 'POST':
        emp_id = request.POST["emp_id"]
        prof = Profile.objects.get(emp_id=emp_id)
        leave_type = request.POST["type"]
        start_date = request.POST["startdate"]
        end_date = request.POST["enddate"]
        no_days = request.POST["leave_days"]
        agent_reason = request.POST["reason"]
        unique_id = request.POST['csrfmiddlewaretoken']

        leaves = LeaveTable.objects.filter(profile=prof).exclude(status="Rejected")
        leave_dates_list = []
        for i in leaves:
            while i.start_date <= i.end_date:
                leave_dates_list.append(i.start_date)
                i.start_date += timedelta(days=1)
        new_leave_dates = []
        list_start_date = datetime.strptime(start_date,
                                            '%Y-%m-%d').date()  # To Convert type of start_date from string to date
        list_end_date = datetime.strptime(end_date,
                                          '%Y-%m-%d').date()  # To Convert type of end_date from string to date
        while list_start_date <= list_end_date:
            new_leave_dates.append(list_start_date)
            list_start_date += timedelta(days=1)

        common_dates = set(leave_dates_list) & set(new_leave_dates)
        if common_dates:
            messages.error(request, "Leaves have already been applied for selected date(s).")
            return redirect('/ams-apply_leave')
        else:
            e = LeaveTable()
            e.unique_id = unique_id
            e.applied_date = datetime.now()
            e.leave_type = leave_type
            e.start_date = start_date
            e.end_date = end_date
            e.no_days = no_days
            e.agent_reason = agent_reason
            e.profile = prof

            # If Only one leave Approval needed
            # e.tl_status = 'Approved'
            # e.tl_approval = True
            # e.tl_reason = 'Self Approved'

            e.save()
            leave_balance = EmployeeLeaveBalance.objects.get(profile=prof)
            if leave_type == 'PL':
                leave_balance.pl_balance -= int(no_days)
                leave_balance.save()
            elif leave_type == 'SL':
                leave_balance.sl_balance -= int(no_days)
                leave_balance.save()

            leave_history = leaveHistory()
            leave_history.leave_type = leave_type
            leave_history.transaction = 'Leave Applied (ID: ' + str(e.id) + ')'
            leave_history.date = date.today()
            leave_history.no_days = int(no_days)
            leave_history.profile = prof
            pl = EmployeeLeaveBalance.objects.get(profile=prof).pl_balance
            sl = EmployeeLeaveBalance.objects.get(profile=prof).sl_balance
            leave_history.total = pl + sl
            leave_history.save()
            return redirect('/ams-apply_leave')
    else:
        profile = request.user.profile
        emp = Profile.objects.get(emp_id=profile.emp_id)
        leave = LeaveTable.objects.filter(profile=profile)
        try:
            Profile.objects.get(emp_id=profile.emp_id, doj=None)
            doj = date(2020, 1, 1)
            today = date.today()
            probation = (today - doj).days
        except Profile.DoesNotExist:
            if emp.doj == None:
                doj = date(2020, 1, 1)
            else:
                doj = emp.doj
            today = date.today()
            probation = (today - doj).days
        try:
            leave_balance = EmployeeLeaveBalance.objects.get(profile=profile)
        except EmployeeLeaveBalance.DoesNotExist:
            leave_balance = {'sl_balance': 0, 'pl_balance': 0}

        leave_his = leaveHistory.objects.filter(profile=profile).values('date', 'transaction',
                                                                        'leave_type', 'total', 'id').annotate(
            no_days=Sum('no_days'))
        data = {'emp': emp, 'leave': leave, 'leave_balance': leave_balance, 'probation': probation,
                'leave_his': leave_his}
        return render(request, 'apply-leave.html', data)


@login_required
def approveLeaveRM1(request):  # Test1
    if request.method == "POST":
        id = request.POST["id"]
        e = LeaveTable.objects.get(id=id)
        emp_id = e.profile.emp_id
        profile = Profile.objects.get(emp_id=emp_id)
        leave_type = e.leave_type
        no_days = e.no_days
        tl_response = request.POST['tl_response']
        tl_reason = request.POST['tl_reason']
        if tl_response == 'Approve':
            tl_approval = True
            tl_status = 'Approved'
            status = 'Pending'
        else:
            tl_approval = True
            tl_status = 'Rejected'
            status = 'Rejected'
            leave_balance = EmployeeLeaveBalance.objects.get(profile=profile)
            if leave_type == 'PL':
                leave_balance.pl_balance += int(no_days)
                leave_balance.save()
            elif leave_type == 'SL':
                leave_balance.sl_balance += int(no_days)
                leave_balance.save()
            leave_history = leaveHistory()
            leave_history.leave_type = leave_type
            leave_history.transaction = 'Leave Refund as RM1 Rejected, Leave applied on: ' + str(
                e.applied_date) + ' (ID: ' + str(e.id) + ')'
            leave_history.date = date.today()
            leave_history.no_days = int(no_days)
            leave_history.profile = e.profile
            pl = EmployeeLeaveBalance.objects.get(profile=profile).pl_balance
            sl = EmployeeLeaveBalance.objects.get(profile=profile).sl_balance
            leave_history.total = pl + sl
            leave_history.save()
        e.tl_approval = tl_approval
        e.tl_reason = tl_reason
        e.tl_status = tl_status
        e.status = status
        e.save()
        return redirect('/view-initial-leave-request')


@login_required
def initialLeaveRequest(request):  # Test1
    emp_id = request.user.profile.emp_id
    profiles = Profile.objects.filter(Q(emp_rm1_id=emp_id))
    profiles_list = []
    for i in profiles:
        profiles_list.append(i)
    leave_request = LeaveTable.objects.filter(Q(profile__in=profiles_list), Q(tl_approval=False),
                                              Q(manager_approval=False))
    data = {'leave_request': leave_request}
    return render(request, 'manager/leave_approval_rm1.html', data)


@login_required
def finalLeaveRequest(request):  # Test1
    if request.method == 'POST':
        id = request.POST["id"]
        e = LeaveTable.objects.get(id=id)
        emp_id = e.profile.emp_id
        team = e.profile.emp_department
        att_actual = e.leave_type
        leave_type = e.leave_type
        no_days = e.no_days
        rm1 = e.profile.emp_rm1
        rm2 = e.profile.emp_rm2
        rm3 = e.profile.emp_rm3
        emp_desi = e.profile.emp_desi
        emp_name = e.profile.emp_name
        now = datetime.now()
        start_date = e.start_date
        end_date = e.end_date
        om_response = request.POST['tl_response']
        om_reason = request.POST['tl_reason']
        if om_response == 'Approve':
            manager_approval = True
            manager_status = 'Approved'
            status = 'Approved'
            month_days = []
            start_date = start_date
            end_date = end_date
            delta = timedelta(days=1)
            while start_date <= end_date:
                month_days.append(start_date.strftime("%Y-%m-%d"))
                start_date += delta
            for i in month_days:
                try:
                    cal = AttendanceCalendar.objects.get(Q(date=i), Q(emp_id=emp_id))
                    cal.att_actual = att_actual
                    cal.appoved_by = request.user.profile.emp_name
                    cal.approved_on = now
                    cal.save()
                except AttendanceCalendar.DoesNotExist:
                    cal = AttendanceCalendar.objects.create(
                        team=team, date=i, emp_id=emp_id,
                        att_actual=att_actual,
                        rm1=rm1, rm2=rm2, rm3=rm3,
                        rm1_id=e.profile.emp_rm1_id, rm2_id=e.profile.emp_rm2_id, rm3_id=e.profile.emp_rm3_id,
                        approved_on=now, emp_desi=emp_desi, appoved_by=request.user.profile.emp_name,
                        emp_name=emp_name
                    )
                    cal.save()

        else:
            manager_approval = True
            manager_status = 'Rejected'
            status = 'Rejected'
            profile = Profile.objects.get(emp_id=emp_id)
            leave_balance = EmployeeLeaveBalance.objects.get(profile=profile)
            if leave_type == 'PL':
                leave_balance.pl_balance += int(no_days)
                leave_balance.save()
            elif leave_type == 'SL':
                leave_balance.sl_balance += int(no_days)
                leave_balance.save()

            leave_history = leaveHistory()
            leave_history.leave_type = leave_type
            leave_history.transaction = 'Leave Refund as RM3 Rejected, Leave applied on: ' + str(
                e.applied_date) + ' (ID: ' + str(e.id) + ')'
            leave_history.date = date.today()
            leave_history.no_days = int(no_days)
            leave_history.profile = e.profile
            pl = EmployeeLeaveBalance.objects.get(profile=profile).pl_balance
            sl = EmployeeLeaveBalance.objects.get(profile=profile).sl_balance
            leave_history.total = pl + sl
            leave_history.save()

        e.manager_approval = manager_approval
        e.manager_reason = om_reason
        e.manager_status = manager_status
        e.status = status
        e.save()
        return redirect('/dashboard')
    else:
        emp_id = request.user.profile.emp_id
        profiles = Profile.objects.filter(Q(emp_rm3_id=emp_id))
        profiles_list = []
        for i in profiles:
            profiles_list.append(i)
        leave_request = LeaveTable.objects.filter(Q(profile__in=profiles_list), Q(tl_approval='Approved'),
                                                  Q(manager_approval=False))
        data = {'leave_request': leave_request}
        return render(request, 'manager/leave_approval_rm3.html', data)


@login_required
def SLProofSubmit(request):  # Test1
    if request.method == 'POST':
        id = request.POST['id']
        proof = request.FILES['proof']
        leave = LeaveTable.objects.get(id=id)
        last_date = leave.end_date
        timee = (date.today() - last_date).days
        if timee <= 2:
            leave.proof = proof
            leave.save()
            return redirect('/ams-apply_leave')
        else:
            messages.info(request, "The time has exceeded cannot upload now :)")
            return redirect('/ams-apply_leave')


@login_required
def applyEscalation(request):  # Test1
    if request.method == "POST":
        id = request.POST["id"]
        reason = request.POST['reason']
        e = LeaveTable.objects.get(id=id)
        e.escalation = True
        e.escalation_reason = reason
        e.save()
        emp_id = e.profile.emp_id
        no_days = e.no_days
        type = e.leave_type
        a = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
        if type == "PL":
            a.pl_balance = a.pl_balance - no_days
        else:
            a.sl_balance = a.sl_balance - no_days
        a.save()

        leave_history = leaveHistory()
        leave_history.leave_type = e.leave_type
        leave_history.transaction = 'Applied for Escalation, Leave applied on: ' + str(e.applied_date) + ' (ID: ' + str(
            e.id) + ')'
        leave_history.date = date.today()
        leave_history.no_days = int(no_days)
        leave_history.emp_id = emp_id
        pl = EmployeeLeaveBalance.objects.get(profile=e.profile).pl_balance
        sl = EmployeeLeaveBalance.objects.get(profile=e.profile).sl_balance
        leave_history.total = pl + sl
        leave_history.save()

        return redirect('/ams-apply_leave')
    else:
        pass


@login_required
def viewEscalation(request):  # Test1
    emp_id = request.user.profile.emp_id
    profiles = Profile.objects.filter(Q(emp_rm3_id=emp_id))
    profiles_list = []
    for i in profiles:
        profiles_list.append(i)
    leave_request = LeaveTable.objects.filter(profile__in=profiles_list, tl_approval=True, escalation=True,
                                              manager_approval=False)
    data = {'leave_request': leave_request}
    return render(request, 'manager/leave_escalation.html', data)


@login_required
def viewLeaveHistory(request):  # Test1
    emp_id = request.user.profile.emp_id
    leave = Profile.objects.filter(Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    direct = LeaveTable.objects.filter(Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    leave_lst = []
    for i in leave:
        under = LeaveTable.objects.filter(Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
        for j in under:
            if j not in leave_lst:
                leave_lst.append(j)
    for i in direct:
        if i not in leave_lst:
            leave_lst.append(i)
    data = {'leave': leave_lst}
    return render(request, 'view_employee_leave_history.html', data)


@login_required
def assetsAssigning(request):
    user = request.user.profile
    if request.method == 'POST':
        unique_id = request.POST['csrfmiddlewaretoken']
        emp_id = request.POST['emp']
        profile = Profile.objects.get(emp_id=emp_id)
        type = request.POST['type']
        given = request.POST['given']
        return_date = request.POST.get('return')
        details = request.POST['details']
        if return_date:
            AssetsDetails.objects.create(
                profile=profile, type=type, given_date=given, return_date=return_date, details=details,
                added_on=datetime.now(), added_by=user.emp_name, added_by_id=user.emp_id, unique_id=unique_id
            )
        else:
            AssetsDetails.objects.create(
                profile=profile, type=type, given_date=given, details=details,
                added_on=datetime.now(), added_by=user.emp_name, added_by_id=user.emp_id, unique_id=unique_id
            )
        messages.info(request, "Added Successfully!.")
        return redirect('/assets')
    else:
        profiles = Profile.objects.all()
        assets = AssetsDetails.objects.all()
        data = {'profiles': profiles, 'assets': assets}
        return render(request, 'hr/assets.html', data)


@login_required
def assetsEdit(request):
    user = request.user.profile
    if request.method == 'POST':
        id = request.POST['id']
        given = request.POST['given']
        return_date = request.POST.get('return')
        details = request.POST['details']
        e = AssetsDetails.objects.get(id=id)
        e.given_date = given
        if return_date:
            e.return_date = return_date
        e.details = details
        e.save()
        return redirect('/assets')
    else:
        messages.info(request, "Invalid Request. you have been logged out!")
        return redirect('/')


@login_required
def assetsDelete(request):
    if request.method == 'POST':
        id = request.POST['id']
        e = AssetsDetails.objects.get(id=id)
        e.delete()
        messages.info(request, 'Successfully Deleted! ')
        return redirect('/assets')
    else:
        messages.info(request, "Invalid Request. you have been logged out!")
        return redirect('/')


@login_required
def applyAttendace(request):  # Test1
    if request.method == 'POST':
        ddate = request.POST['date']
        att_actual = request.POST['att_actual']
        emp_id = request.POST['emp_id']
        now = datetime.now()
        prof = Profile.objects.get(emp_id=emp_id)
        rm1 = prof.emp_rm1
        rm2 = prof.emp_rm2
        rm3 = prof.emp_rm3
        rm1_id = prof.emp_rm1_id
        rm2_id = prof.emp_rm2_id
        rm3_id = prof.emp_rm3_id
        desi = prof.emp_desi
        team = prof.emp_department
        team_id = prof.emp_department_id
        try:
            cal = AttendanceCalendar.objects.get(Q(date=ddate), Q(emp_id=emp_id), ~Q(att_actual='Unmarked'))
            messages.info(request, '*** Already Marked in Calendar, Please Refresh the page and try again ***')
            return redirect('/team-attendance')
        except AttendanceCalendar.DoesNotExist:
            cal = AttendanceCalendar.objects.get(emp_id=emp_id, date=ddate)
            cal.att_actual = att_actual
            cal.approved_on = now
            cal.appoved_by = request.user.profile.emp_name
            cal.rm1 = rm1
            cal.rm2 = rm2
            cal.rm3 = rm3
            cal.rm1_id = rm1_id
            cal.rm2_id = rm2_id
            cal.rm3_id = rm3_id
            cal.emp_desi = desi
            cal.team = team
            cal.team_id = team_id
            cal.save()
        if att_actual == 'Attrition' or att_actual == 'Bench':
            usr = Profile.objects.get(emp_id=emp_id)
            usr.agent_status = att_actual
            usr.save()
        if att_actual == 'NCNS':
            today = date.today()
            yesterday = today - timedelta(days=1)
            dby_date = yesterday - timedelta(days=1)
            date_range = [dby_date, today]
            ncns_count = AttendanceCalendar.objects.filter(emp_id=emp_id, date__range=date_range,
                                                           att_actual='NCNS').count()
            if ncns_count >= 3:
                usr = Profile.objects.get(emp_id=emp_id)
                usr.agent_status = att_actual
                usr.save()

        return redirect('/attendance')
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        dby_date = yesterday - timedelta(days=1)
        emp_id = request.user.profile.emp_id
        # Today
        todays_list_list = AttendanceCalendar.objects.filter(Q(date=today), Q(emp_id=emp_id), Q(att_actual='Unmarked'))
        # Yesterday
        ystday_list_list = AttendanceCalendar.objects.filter(Q(date=yesterday), Q(emp_id=emp_id),
                                                             Q(att_actual='Unmarked'))
        # Day before yesterday
        dby_list_list = AttendanceCalendar.objects.filter(Q(date=dby_date), Q(emp_id=emp_id), Q(att_actual='Unmarked'))
        emp = Profile.objects.get(emp_id=emp_id)
        data = {'todays_att': todays_list_list, 'ystdays_att': ystday_list_list, 'dbys_att': dby_list_list, 'emp': emp}
        return render(request, 'attendance.html', data)


@login_required
def viewTeamAttendance(request):  # Test1
    if request.method == 'POST':
        rm = request.user.profile.emp_id
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        emp_id = request.POST['emp_id']
        if emp_id == 'All':
            if request.user.profile.emp_desi in manager_list:
                all_emp = Profile.objects.filter(Q(emp_rm1_id=rm) | Q(emp_rm2_id=rm) | Q(emp_rm3_id=rm))
                emp_id_lst = []
                for i in all_emp:
                    if i.emp_id not in emp_id_lst:
                        emp_id_lst.append(i.emp_id)
                        under = Profile.objects.filter(
                            Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
                        for j in under:
                            if j.emp_id not in emp_id_lst:
                                emp_id_lst.append(j.emp_id)
                # cal = EcplCalander.objects.filter(emp_id__in=emp_id_lst,
                #        date__range=[start_date, end_date])
                # Export
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
                writer = csv.writer(response)
                writer.writerow(
                    ['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
                calanders = AttendanceCalendar.objects.filter(
                    emp_id__in=emp_id_lst, date__range=[start_date, end_date]).values_list(
                    'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
                for c in calanders:
                    writer.writerow(c)
                return response
            else:
                # cal = EcplCalander.objects.filter(Q(rm1_id=rm) | Q(rm2_id=rm) | Q(rm3_id=rm),
                #                              date__range=[start_date, end_date])
                # Export
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
                writer = csv.writer(response)
                writer.writerow(
                    ['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
                calanders = AttendanceCalendar.objects.filter(
                    Q(rm1_id=rm) | Q(rm2_id=rm) | Q(rm3_id=rm), date__range=[start_date, end_date]).values_list(
                    'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
                for c in calanders:
                    writer.writerow(c)
                return response

        else:
            cal = AttendanceCalendar.objects.filter(date__range=[start_date, end_date], emp_id=emp_id)
        if emp_id == 'self':
            cal = AttendanceCalendar.objects.filter(emp_id=rm, date__range=[start_date, end_date])
        emp = Profile.objects.get(emp_id=rm)
        data = {'agt_cal_list': cal, 'emp': emp}
        return render(request, 'agent-calander-status.html', data)
    else:
        messages.info(request, "Invalid Request!")
        return redirect('/dashboard')


@login_required
def weekAttendanceReport(request):  # Test1
    def Merge(a, b, c, d, e, f, g):
        res = {**a, **b, **c, **d, **e, **f, **g}
        return res

    empobj = Profile.objects.get(emp_id=request.user.profile.emp_id)
    emp_id = request.user.profile.emp_id
    day = date.today()
    start = day - timedelta(days=day.weekday())
    start = start + timedelta(days=-1)
    start_year = start.year
    start_month = start.month
    start_day = start.day
    end = start + timedelta(days=6)
    start = date(start_year, start_month, start_day)
    end_year = end.year
    end_month = end.month
    end_day = end.day
    end = date(end_year, end_month, end_day)
    weeks = ['sund', 'mon', 'tue', 'wed', 'thur', 'fri', 'sat']
    emp_id_list = []
    ems = Profile.objects.filter(
        Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id), Q(agent_status='Active')
    )
    for i in ems:
        if i.emp_id not in emp_id_list:
            emp_id_list.append(i.emp_id)
    weekdays = []
    delta = timedelta(days=1)
    while start <= end:
        weekdays.append(start)
        start += delta
    lst = []  # main data
    calobj = AttendanceCalendar.objects.filter(emp_id__in=emp_id_list, date__in=weekdays)
    for i in calobj:
        samp = {}
        samp['name'] = i.emp_name
        samp["emp_id"] = i.emp_id
        samp[i.date] = i.att_actual
        lst.append(samp)
    n = 0
    new_lst = []
    sort = sorted(lst, key=lambda x: x['emp_id'])

    for i in range(0, len(emp_id_list)):
        individual = Merge(sort[n], sort[n + 1], sort[n + 2], sort[n + 3], sort[n + 4], sort[n + 5], sort[n + 6])
        j = 0
        for w in weekdays:
            a = weeks[j]
            individual[a] = individual[w]
            del individual[w]
            j += 1
        new_lst.append(individual)
        n += 7

    data = {"cal": new_lst, 'emp': empobj}
    return render(request, 'week_attendace_report.html', data)


@login_required
def teamAttendanceReport(request):  # Test 1
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        team_name = request.POST['team_name']
        start_date = start_date
        end_date = end_date
        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        if team_name == 'All Team':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
            calanders = AttendanceCalendar.objects.filter(date__range=[start_date, end_date]).values_list(
                'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
            for c in calanders:
                writer.writerow(c)
            return response
        else:
            team_name = Departments.objects.get(id=team_name).name
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
            calanders = AttendanceCalendar.objects.filter(team=team_name,
                                                          date__range=[start_date, end_date]).values_list(
                'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
            for c in calanders:
                writer.writerow(c)
            return response
    else:
        return HttpResponse('<h2>*** GET not available ***</h2>')


@login_required
def Settings(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    data = {'emp': emp, 'form': form}
    return render(request, 'settings.html', data)


@login_required
def uploadImageToDB(request):  # Test1
    if request.method == 'POST':
        user_image = request.FILES['user-img']
        id = request.POST['id']
        prof = Profile.objects.get(id=id)
        prof.img = user_image
        prof.save()
        return redirect('/dashboard')
    else:
        messages.error(request, 'Invalid Request :)')
        return redirect('/')


@login_required
def addNewUser(request):  # Test1  # calander pending
    if request.method == 'POST':
        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        emp_doj = request.POST["emp_doj"]
        emp_dob = request.POST["emp_dob"]
        emp_desi = request.POST["emp_desg"]
        emp_rm1_id = request.POST["emp_rm1_id"]
        emp_rm2_id = request.POST["emp_rm2_id"]
        emp_rm3_id = request.POST["emp_rm3_id"]
        emp_rm1 = Profile.objects.get(emp_id=emp_rm1_id)
        emp_rm2 = Profile.objects.get(emp_id=emp_rm2_id)
        emp_rm3 = Profile.objects.get(emp_id=emp_rm3_id)
        emp_process_id = request.POST["emp_pro"]
        emp_process = Departments.objects.get(id=emp_process_id).name
        usr = User.objects.filter(username=emp_id)
        if usr.exists():
            messages.info(request, "***User Already Exists***")
            return redirect("/add-new-user")
        else:
            # Creating User
            user = User.objects.create_user(username=emp_id, password=str(emp_id))
            # Creating Profile
            profile = Profile.objects.create(
                user=user, emp_id=emp_id, emp_name=emp_name, emp_desi=emp_desi,
                emp_rm1=emp_rm1, emp_rm2=emp_rm2, emp_rm3=emp_rm3, emp_rm1_id=emp_rm1_id, emp_rm2_id=emp_rm2_id,
                emp_rm3_id=emp_rm3_id, emp_department=emp_process, emp_department_id=emp_process_id, doj=emp_doj,
                dob=emp_dob
            )
            # Creating Leave Balance
            EmployeeLeaveBalance.objects.create(
                profile=profile, pl_balance=0, sl_balance=0
            )
            # Creating Attendance
            start_date = datetime.strptime(emp_doj, '%Y-%m-%d').date()
            last_date = date.today() + monthdelta(2)
            last_date = date(last_date.year, last_date.month, 1) - timedelta(days=1)
            delta = last_date - start_date
            date_list = []
            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                date_list.append(day)
            j = Profile.objects.get(emp_id=emp_id)
            for i in date_list:
                try:
                    AttendanceCalendar.objects.get(emp_id=j.emp_id, date=i)
                except AttendanceCalendar.DoesNotExist:
                    AttendanceCalendar.objects.create(date=i, emp_id=j.emp_id, att_actual='Unmarked',
                                                      emp_name=j.emp_name, emp_desi=j.emp_desi,
                                                      team=j.emp_department, team_id=j.emp_department_id, rm1=j.emp_rm1,
                                                      rm2=j.emp_rm2, rm3=j.emp_rm3, rm1_id=j.emp_rm1_id,
                                                      rm2_id=j.emp_rm2_id, rm3_id=j.emp_rm3_id)
            date_list_week = []
            if start_date.weekday() != 6:
                for i in range(1, start_date.weekday() + 2):
                    date_list_week.append(start_date - timedelta(days=i))
            for i in date_list_week:
                try:
                    AttendanceCalendar.objects.get(emp_id=j.emp_id, date=i)
                except AttendanceCalendar.DoesNotExist:
                    AttendanceCalendar.objects.create(date=i, emp_id=j.emp_id, att_actual='',
                                                      emp_name=j.emp_name, emp_desi=j.emp_desi,
                                                      team=j.emp_department, team_id=j.emp_department_id, rm1=j.emp_rm1,
                                                      rm2=j.emp_rm2, rm3=j.emp_rm3, rm1_id=j.emp_rm1_id,
                                                      rm2_id=j.emp_rm2_id, rm3_id=j.emp_rm3_id)
        messages.info(request, 'User and Profile Successfully Created')
        return redirect('/add-new-user')
    else:
        all_desi = Designation.objects.all()
        rms = Profile.objects.all()
        all_team = Departments.objects.all()

        # onboarding = OnboardingnewHRC.objects.filter(user_created=False)
        data = {'all_data': all_desi, 'rms': rms, 'all_team': all_team, }
        return render(request, 'hr/add_user.html', data)


@login_required
def addNewDesi(request):
    if request.method == 'POST':
        name = request.POST['new_desg']
        try:
            Designation.objects.get(name__iexact=name)
            messages.success(request, "Designation with same name already present!")
            return redirect('/add-new-user')
        except Designation.DoesNotExist:
            Designation.objects.create(name=name, created_by=request.user.profile.emp_name)
            messages.success(request, "New Designation Added!")
            return redirect('/add-new-user')
    else:
        messages.error(request, "Invalid request! you have been logged out")
        return redirect('/')


@login_required
def viewUsersHR(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    add = Profile.objects.all()
    data = {'add': add, 'emp': emp}
    return render(request, 'hr/view_users.html', data)


@login_required
def viewEmployeeProfile(request, id, on_id):  # Test 1
    if request.method == 'POST':
        changed_name = request.POST.get('emp_name')
        changed_desi = request.POST.get('emp_desi')
        type = request.POST['from']
        if type == 'name':
            n = Profile.objects.get(id=id)
            n.emp_name = changed_name
            n.save()
            x = Profile.objects.filter(Q(emp_rm1_id=n.emp_id) | Q(emp_rm2_id=n.emp_id) | Q(emp_rm3_id=n.emp_id))
            change = []
            for i in x:
                if i.emp_rm1_id == n.emp_id:
                    i.emp_rm1 = changed_name
                if i.emp_rm2_id == n.emp_id:
                    i.emp_rm2 = changed_name
                if i.emp_rm3_id == n.emp_id:
                    i.emp_rm3 = changed_name
                change.append(i)
            Profile.objects.bulk_update(change, ['emp_rm1', 'emp_rm2', 'emp_rm3'])
            messages.success(request, 'Employee Name Changed Successfully!')
            return redirect('/view-employee-profile/' + str(id) + '/' + str(on_id))
        elif type == 'desi':
            n = Profile.objects.get(id=id)
            n.emp_desi = changed_desi
            n.save()
            messages.success(request, 'Employee Designation Changed Successfully!')
            return redirect('/view-employee-profile/' + str(id) + '/' + str(on_id))

    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    profile = Profile.objects.get(id=id)
    if on_id == "None":
        onboarding = ""
    # else:
    #     onboarding = OnboardingnewHRC.objects.get(id=int(on_id))
    rms = Profile.objects.exclude(emp_desi__in=agent_list)
    designations = Designation.objects.all()
    departments = Departments.objects.all()
    data = {'profile': profile, 'onboard': onboarding, 'emp': emp, "on": on_id, "hr_list": hr_list,
            'designations': designations, 'rms': rms, 'departments': departments}
    return render(request, 'emp_profile_view.html', data)


@login_required
def changeMapping(request):
    if request.method == "POST":
        id = request.POST["id"]
        rm1 = request.POST["rm1"]
        rm1 = Profile.objects.get(id=rm1)
        rm2 = request.POST["rm2"]
        rm2 = Profile.objects.get(id=rm2)
        rm3 = request.POST["rm3"]
        rm3 = Profile.objects.get(id=rm3)
        emp_department = request.POST["emp_department"]
        emp_department = Departments.objects.get(id=emp_department).name
        e = Profile.objects.get(id=id)
        e.emp_rm1 = rm1.emp_name
        e.emp_rm1_id = rm1.emp_id
        e.emp_rm2 = rm2.emp_name
        e.emp_rm2_id = rm2.emp_id
        e.emp_rm3 = rm3.emp_name
        e.emp_rm3_id = rm3.emp_id
        e.emp_department = emp_department
        e.save()
        messages.success(request, 'Successfully Changed!')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Bad Request!')
        return redirect('/dashboard')

@login_required
def editAgentStatus(request):  # Test1
    if request.method == 'POST':
        id = request.POST['id']
        agent_status = request.POST['new_status']
        profile = Profile.objects.get(id=id)
        profile.agent_status = agent_status
        profile.save()
        return redirect('/viewusers')
    else:
        messages.error(request, 'Bad Request!')
        return redirect('/dashboard')

@login_required
def addNewTeam(request):  # Test1
    if request.method == "POST":
        usr = request.user.profile.emp_name
        om = request.POST["om"]
        campaign = request.POST["campaign"]
        try:
            Departments.objects.get(name__iexact=campaign)
            messages.info(request, 'Team ' + campaign + 'Not added as Already Present')
            return redirect('/view-all-teams')
        except Departments.DoesNotExist:
            name = Profile.objects.get(emp_id=om).emp_name
            cam = Departments.objects.create(name=campaign, om=name, created_by=usr)
            cam.save()
            messages.info(request, 'Team ' + campaign + ' Created Successfully')
            return redirect('/departments')
    else:
        messages.error(request, 'Invalid Request :)')
        return redirect('/view-all-teams')


@login_required
def viewTeam(request):  # Test1
    teams = Departments.objects.all()
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    managers = Profile.objects.all()
    data = {'teams': teams, 'emp': emp, 'managers': managers}
    return render(request, 'hr/view_team.html', data)


@login_required
def viewallOMS(request, name):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    all_emp = Profile.objects.filter(Q(agent_status='Active'),
                                     Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    all_emps_under = []
    for i in all_emp:
        if i not in all_emps_under:
            all_emps_under.append(i)
            under = Profile.objects.filter(Q(agent_status='Active'),
                                           Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
            for j in under:
                if j not in all_emps_under:
                    all_emps_under.append(j)
    if name == 'Agent':
        all_emps_under = all_emps_under
        data = {'emp': emp, 'all_emp': all_emps_under}
        return render(request, 'view_emps.html', data)
    elif name == 'TL':
        all_tls_under = []
        for i in all_emps_under:
            if i not in all_tls_under:
                if i.emp_desi == 'Team Leader':
                    all_tls_under.append(i)
        data = {'emp': emp, 'all_emp': all_tls_under}
        return render(request, 'view_emps.html', data)
    elif name == 'AM':
        all_ams_under = []
        for i in all_emps_under:
            if i not in all_ams_under:
                if i.emp_desi == 'Assistant Manager':
                    all_ams_under.append(i)
        data = {'emp': emp, 'all_emp': all_ams_under}
        return render(request, 'view_emps.html', data)
    else:
        messages.info(request, 'Bad Request')
        return redirect('/dashboard')


def testFun(request):
    mydate = date.today()
    month = mydate.month
    year = mydate.year
    start_date = date(2022, 5, 1)
    # start_date += monthdelta.monthdelta(1)
    # last = calendar.monthrange(year, month)[1]
    last_date = date(2022, 6, 30)
    # last_date += monthdelta.monthdelta(1)
    delta = last_date - start_date
    date_list = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_list.append(day)
    for i in date_list:
        profile = Profile.objects.all().exclude(
            emp_id__in=AttendanceCalendar.objects.filter(date=i).values('emp_id'), agent_status='Attrition')
        cal = []
        for j in profile:
            employees = AttendanceCalendar()
            employees.date = i
            employees.emp_id = j.emp_id
            employees.att_actual = 'Unmarked'
            employees.emp_name = j.emp_name
            employees.emp_desi = j.emp_desi
            employees.team = j.emp_department
            employees.team_id = j.emp_department_id
            employees.rm1 = j.emp_rm1
            employees.rm2 = j.emp_rm2
            employees.rm3 = j.emp_rm3
            employees.rm1_id = j.emp_rm1_id
            employees.rm2_id = j.emp_rm2_id
            employees.rm3_id = j.emp_rm3_id
            cal.append(employees)
        AttendanceCalendar.objects.bulk_create(cal)
    return redirect('/dashboard')


@login_required
def Reimbursement(request):
    profile = request.user.profile
    if request.method == "POST":
        date = request.POST["date"]
        type = request.POST["type"]
        amount = request.POST["amount"]
        bill = request.FILES["bill"]
        details = request.POST["details"]
        ReimbursementTickets.objects.create(
            profile=profile, date_for=date, type=type, amount=amount, bill=bill, details=details
        )
        return redirect('/reimbursement')
    else:
        tickets = ReimbursementTickets.objects.filter(profile=profile)
        data = {'tickets': tickets}
        return render(request, 'reimbursement.html', data)


@login_required
def editReimbursement(request):
    if request.method == "POST":
        id = request.POST["id"]
        datee = request.POST.get("date")
        type = request.POST.get("type")
        amount = request.POST.get("amount")
        bill = request.FILES.get("bill")
        details = request.POST.get("details")
        e = ReimbursementTickets.objects.get(id=id)
        if datee:
            e.date_for = datee
        if type:
            e.type = type
        if amount:
            e.amount = amount
        if bill:
            e.bill = bill
        if details:
            e.details = details
        e.save()
        return redirect('/reimbursement')
    else:
        messages.info(request, 'Bad Request')
        return redirect('/dashboard')


@login_required
def deleteReimbursement(request):
    if request.method == "POST":
        id = request.POST["id"]
        e = ReimbursementTickets.objects.get(id=id)
        os.remove("media/" + str(e.bill))
        e.delete()
        return redirect('/reimbursement')
    else:
        messages.info(request, 'Bad Request')
        return redirect('/dashboard')


@login_required
def viewReimbursement(request):
    if request.method == "POST":
        id = request.POST["id"]
        response = request.POST.get("response")
        approval_comments = request.POST.get("comments")
        e = ReimbursementTickets.objects.get(id=id)
        if response:
            e.approved_by = request.user.profile.emp_name
            e.approved_by_id = request.user.profile.emp_id
            e.approved_on = date.today()
            e.approval_comments = approval_comments
            e.respond = True
            e.status = response
        e.save()
        return redirect('/view-reimbursement')
    else:
        emp_id = request.user.profile.emp_id
        profiles = Profile.objects.filter(Q(emp_rm1_id=emp_id) | Q(emp_rm3_id=emp_id) | Q(emp_rm3_id=emp_id))
        tickets = ReimbursementTickets.objects.filter(profile__in=profiles, respond=False)
        data = {'tickets': tickets}
        return render(request, 'manager/view_reimbursement.html', data)
