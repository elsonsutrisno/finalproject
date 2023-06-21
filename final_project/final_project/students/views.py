from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import user_passes_test
from django.db import transaction
from django.contrib import messages
from .utils import *
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test

def check_student_role(user):
    return user.role == 'student' or user.role == 'dosen'

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return login_required(
            user_passes_test(
                check_student_role,
                login_url='login'
            )(view_func)
        )(request, *args, **kwargs)
    return wrapper

@student_required
def students_index(request):
    time_ordered, session = get_order_time(request.user.id)
    context = get_student_dininghall_context(request)
    context['fullname'] =  request.user.name
    context['time_suggested'] : time_ordered
    context['session'] : session
    
    return render(request, "students/student_index.html", context )

@student_required
def menu(request):
    context = get_student_dininghall_context(request)
    return render(request, 'students/menu.html', context)

@student_required
def students_home_view_dininghall(request):
    context = get_student_dininghall_context(request)
    return render(request, 'students/student_dininghall_view.html', context)

@student_required
def students_home_view_library(request):
    return render(request, 'students/student_library_view.html')

@student_required
def students_home_view_laboratorium(request):
    return render(request, 'students/student_laboratorium_view.html')

@student_required
@transaction.atomic
def confirm_action(request, current_hour, current_date, session_name, time_objects, session_id):
    context = None
    session_id = get_session_id_based_date_and_session_name(current_date, session_name)
    time_suggested = request.POST.get('time_suggested')
    choice = request.POST.get('choice')
    if choice == 'no':
        context = {
            'time_objects': time_objects,
            'session_id': session_id,
            'time_suggested': time_suggested,
            'session': session_name,
            'date': current_date,
            'current_hour': current_hour,
            'can_booking': True
        }
        
        return render(request, 'students/student_preferences.html', context)
    
    # if is_session_id_in_booking_table(session_id):
    #     context = None
    #     return render(request, 'students/student_preferences.html', context)
    
    time_object = get_time_by_session_id_and_suggested_time(time_suggested, session_id)
    print(time_object, time_suggested, session_id)
    if time_object is not None: 
        update_available_seats(time_object)
        user_object = get_userobject_by_id(request.user.id)
        create_booking(user_object, session_id, time_suggested)
        print('booking success')
    # update_seat_availability(time_suggested, new_availability_seat)
    messages.success(request, "Booking Success", extra_tags="success")
    return redirect('student_index') 

@student_required
@transaction.atomic
def cancel_order(request):
    user_id = request.user.id
    # DELETE and UPDATE Database
    message = delete_booking_and_update_available_seat_by_user_id(user_id)
    messages.success(request, message, extra_tags="success")
    
    return redirect("student_index")

@student_required
@transaction.atomic
def student_preferences(request):
    if request.method == 'POST':
        is_take = request.POST.get('take')
        if is_take:

            start_time = request.POST.get('start_range')
            end_time = request.POST.get('end_range')

            session_pref = request.POST.get('session_pref')
            date_pref = request.POST.get('date_pref')
            date_pref = datetime.strptime(date_pref, "%Y-%m-%d").date()

            current_hour, current_date = get_current_hour_and_current_date()
            session, time_objects = get_session_and_time_objects(current_hour)

            session = session_pref
            current_date = date_pref

            session_id = get_session_id_based_date_and_session_name(current_date, session)
            session_info = get_session_time_and_seat(get_session_id(current_date, session))
            suggested_time = get_recommended_time(session_info, start_time, end_time)
            menus = get_menu_based_date(current_date)
            breakfast, lunch, dinner = return_menus_for_each_session_in_one_date(menus)
            context = {
                'time_objects': time_objects,
                'session_id': session_id,
                'time_suggested': suggested_time,
                'session': session,
                'date': current_date,
                'day': current_date.strftime('%A'),
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'can_booking': True,
                'current_session' : session.upper()
            }
            return render(request, 'students/student_preferences.html', context)
    
    if request.method == 'GET':
        
        start_time = request.POST.get('start_range')
        end_time = request.POST.get('end_range')

        current_hour, current_date = get_current_hour_and_current_date()
        session, time_objects = get_session_and_time_objects(current_hour)

        session_id = get_session_id_based_date_and_session_name(current_date, session)
        session_info = get_session_time_and_seat(get_session_id(current_date, session))

        request.POST.get('time_suggested')
        context = {
                'time_objects': time_objects,
                'session_id': session_id,
                'time_suggested': "NotSearched",
                'session': session,
                'date': current_date,
                'day': current_date.strftime('%A'),
                'can_booking': True,
                'current_session' : session.upper()
            }
        return render(request, 'students/student_preferences.html', context)
    
@student_required
def confirm(request):
    current_hour, current_date = get_current_hour_and_current_date()
    session, time_objects = get_session_and_time_objects(current_hour)
    session_id = get_session_id_based_date_and_session_name(current_date, session)

    return confirm_action(request, current_hour, current_date, session, time_objects, session_id)

def not_student(request):
    messages.error(request, 'You are not authorized to access student resources. You need the Student role.')
    return redirect('dininghall_index')
