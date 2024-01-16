from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import date
from django import forms
from django.core import exceptions
from mon_site.models import Person, Student, Employee, Message
from mon_site.forms import StudentProfileForm, EmployeeProfileForm, LoginForm, AddFriendForm


# Create your views here.
# register views

from django.shortcuts import render, redirect
from .forms import StudentProfileForm, EmployeeProfileForm

def register(request):
    studentForm = StudentProfileForm(prefix="st")
    employeeForm = EmployeeProfileForm(prefix="em")

    if request.method == 'GET' and 'profileType' in request.GET:
        profile_type = request.GET['profileType']

        if profile_type == 'student':
            studentForm = StudentProfileForm(request.GET, prefix="st")
            if studentForm.is_valid():
                studentForm.save()
                return redirect('login')
        elif profile_type == 'employee':
            employeeForm = EmployeeProfileForm(request.GET, prefix="em")
            if employeeForm.is_valid():
                employeeForm.save()
                return redirect('login')
        # le formulaire n'est pas valide
    return render(request, 'user_profile.html', {'studentForm': studentForm, 'employeeForm': employeeForm})
    
# login views

def login(request):
    # Teste si formulaire a été envoyé
    if len(request.POST) > 0:
        form = LoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            logged_user = Person.objects.get(email=user_email)
            request.session['logged_user_id'] = logged_user.id
            return redirect('welcome')
        else:
            return render(request,'login.html',{'form':form})
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


# protection des pages privées
def get_logged_user_from_request(request):
    if 'logged_user_id' in request.session:
        logged_user_id = request.session['logged_user_id']
        # on cherche un etudiant
        if len(Student.objects.filter(id=logged_user_id)) == 1:
            return Student.objects.get(id=logged_user_id)
        # On cherche un employé
        elif len(Employee.objects.filter(id=logged_user_id)) == 1:
            return Employee.objects.get(id=logged_user_id)
        # Si on n'a rien trouve
        else:
            return None
    else:
        return None 
    
# welcome views

def welcome(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if 'newMessage' in request.GET and request.GET['newMessage'] != '':
            newMessage = Message(author=logged_user,content=request.GET['newMessage'],publication_date = date.today())
            newMessage.save()
        friendMessages = Message.objects.filter(author__friends=logged_user).order_by('-publication_date')

        return render(request, 'welcome.html', {'logged_user':logged_user,'friendMessages':friendMessages})
    else:
        return redirect('login')

def add_friend(request):
    logged_user = get_logged_user_from_request(request)

    if logged_user:
        # Vérifie si le formulaire a été envoyé
        if len(request.POST) > 0:
            form = AddFriendForm(request.GET)
            if form.is_valid():
                new_friend_email = form.cleaned_data['email']
                new_friend = Person.objects.get(email=new_friend_email)
                logged_user.friends.add(new_friend)
                logged_user.save()
                return redirect('/welcome')
            else:
                return render(request, 'add_friend.html', {'form': form})
        # Le formulaire n'a pas été envoyé
        else:
            form = AddFriendForm()
            return render(request, 'add_friend.html', {'form': form})
    else:
        return redirect('/login')
 
def show_profile(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if 'userToShow' in request.GET and request.GET['userToShow'] != '':
            user_to_show_id = int(request.GET['userToShow'])
            results = Person.objects.filter(id=user_to_show_id)
            if len(results) == 1:
                if Student.objects.filter(id=user_to_show_id):
                    user_to_show = Student.objects.get(id=user_to_show_id)
                else:
                    user_to_show = Employee.objects.get(id=user_to_show_id)
                return render(request, 'show_profile.html',{'user_to_show':user_to_show})
            else:
                return render(request, 'show_profile.html',{'user_to_show':logged_user})
        else:
            return render(request, 'show_profile.html',{'user_to_show':logged_user})
    else:
        return redirect('login')
                
                

def modify_profile(request):
    logged_user = get_logged_user_from_request(request)
    if logged_user:
        if len(request.GET) > 0:
            if type(logged_user) == Student:
                form = StudentProfileForm(request.GET, instance=logged_user)
            else:
                form = EmployeeProfileForm(request.GET, instance=logged_user)
            if form.is_valid():
                form.save()
                return redirect('/welcome')
            else:
                return render(request, 'modify_profile.html', {'form':form})
        else:
            if type(logged_user) == Student:
                form = StudentProfileForm(request.GET, instance=logged_user)
            else:
                form = EmployeeProfileForm(request.GET, instance=logged_user)
            return render(request, 'modify_profile.html', {'form':form})
    else:
        return redirect('/login')
    
def ajax_check_email_field(request):
    html_to_return = ''
    if 'value' in request.GET:
        field = forms.EmailField()
        try:
            field.clean(request.GET['value'])
        except forms.ValidationError as ve:
            html_to_return = '<ul class="errorlist">'
            for message in ve.messages:
                html_to_return += '<li>' + message + '</li>'
            html_to_return += '</ul>'

        if len(html_to_return) == 0:
            if len(Person.objects.filter(email=request.GET['value']))  >= 1:
                html_to_return = '<ul class="errorlist">'
                html_to_return += '<li> Cette adresse est déjà utilisée!</li>'
                html_to_return += '</ul>'
    return HttpResponse(html_to_return)

def ajax_add_friend(request):
    html_to_return= ''
    logged_user = get_logged_user_from_request(request)
    if logged_user is not None:
        if 'email' in request.GET:
            new_friend_email = request.GET['email']
            if len(Person.objects.filter(email=new_friend_email)) == 1:
                new_friend = Person.objects.get(email=new_friend_email)
                logged_user.friends.add(new_friend)
                logged_user.save()

                html_to_return = '<li><a href="show_profile?userToShow='
                html_to_return += str(new_friend.id)
                html_to_return += '">'
                html_to_return += new_friend.first_name + ' ' + new_friend.last_name
                html_to_return += '</a></li>'
    return HttpResponse(html_to_return)
