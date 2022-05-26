import json
from datetime import date, timedelta
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from monthdelta import monthdelta
import calendar

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
        messages.info(request,'Invalid Request.')
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
        login_id = login.logout - login.login
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
    data = {'login': login, 'login_id': login_id, 'birthdays': birthdays, 'new_joins': new_joins, 'month_cal': month_cal}
    return render(request, 'hr/hr_dashboard.html', data)


@login_required
def agentDashBoard(request):  # Test1 Test2
    if request.user.profile.emp_desi in agent_list:
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
        data = {'emp': emp, 'leave_hist': leave_hist, 'month_cal': month_cal}
        return render(request, 'agent/agent-dashboard.html', data)
    else:
        messages.error(request, 'Unauthorized access. You have been Logged Our !')
        return redirect('')


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
        return redirect('/hr-dashboard')
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
            return redirect('/ams/ams-apply_leave')
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
            # rm1_desi = Profile.objects.get(emp_id=emp_rm1_id).emp_desi
            #
            # if rm1_desi in manager_list or rm1_desi in hr_om_list:
            #     e.tl_status = 'Approved'
            #     e.tl_approval = True
            #     e.tl_reason = 'OM as TL'
            # if emp_desi in manager_list or emp_desi in tl_am_list or emp_desi in hr_tl_am_list or emp_desi in hr_om_list:
            #     e.tl_status = 'Approved'
            #     e.tl_approval = True
            #     e.tl_reason = 'Self Approved'
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
            return redirect('/ams/team-attendance')
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
            return redirect('/ams/add-new-user')
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
            return redirect('/view-all-teams')
    else:
        messages.error(request, 'Invalid Request :)')
        return redirect('/view-all-teams')


@login_required
def viewTeam(request):  # Test1
    teams = Departments.objects.all()
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    managers = Profile.objects.all()
    data = {'teams': teams, 'emp': emp, 'managers':managers}
    return render(request, 'hr/view_team.html', data)

