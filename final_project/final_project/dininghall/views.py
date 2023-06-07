from django.shortcuts import render, redirect
from .forms import SessionForm, TimeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import user_passes_test
from django.http import HttpResponse
from django.db import transaction
from .utils import *
import os

def check_dininghall_role(user):
    return user.role == 'dininghall'

@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
def dininghall_index(request):
    session_objects = get_all_session_objects()
    session_ids = [session.id for session in session_objects]
    time_objects = []

    for session_id in session_ids:
        time_objects.append((session_id, get_time_objects(session_id)))

    context = {"session_objects": session_objects, "time_objects": time_objects}
    return render(request, "dininghall/dininghall_index.html", context)


@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
@transaction.atomic
def add_session(request):
    submitted = False
    if request.method == "POST":
        form_session = SessionForm(request.POST)
        form_time = TimeForm(request.POST)
        if form_session.is_valid() and form_time.is_valid():
            save_session_and_times(form_session, form_time)
            return redirect("dininghall_index")
    else:
        form_session = SessionForm()
        form_time = TimeForm()
        if "submitted" in request.GET:
            submitted = True
    return render(request, "dininghall/add_menu.html", {"form_session": form_session, "form_time": form_time, "submitted": submitted})

@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
@transaction.atomic
def edit_session(request, session_id):
    session = get_session_by_id(session_id)
    form = SessionForm(request.POST or None, instance=session)
    if form.is_valid():
        update_session(form)
        return redirect('dininghall_index')
    return render(request, 'dininghall/edit_menu.html', {'menu': session, 'form': form})

@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
@transaction.atomic
def delete_session(request, session_id):
    session = get_session_by_id(session_id)
    delete_session_object(session)
    return redirect('dininghall_index')

@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
@transaction.atomic
def edit_time(request, time_id):
    time = get_time_by_id(time_id)
    form = TimeForm(request.POST or None, instance=time)
    if form.is_valid():
        update_session(form)
        return redirect('dininghall_index')
    return render(request, 'dininghall/edit_menu.html', {'time_objects': time, 'form': form})

@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
@transaction.atomic
def delete_time(request, time_id):
    session = get_time_by_id(time_id)
    delete_time_object(session)
    return redirect('dininghall_index')

@login_required(login_url='login')
@user_passes_test(check_dininghall_role, login_url='not_dininghall')
def export_order_record(request):
    # File path where the Excel file will be saved
    file_path = "order_record.xlsx"

    # Export data to the Excel file
    export_data_to_excel(file_path)

    # Open the file in binary mode and read its contents
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Set the appropriate response headers for file download
    response = HttpResponse(file_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="order_record.xlsx"'

    # Delete the file from the server
    os.remove(file_path)

    return response

def not_dininghall(request):
    messages.error(request, 'You are not authorized to access dining hall resources. You need the Dining Hall role.')
    return redirect('student_index')
