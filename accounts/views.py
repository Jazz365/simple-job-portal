from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only

@unauthenticated_user
def registerPage(request):

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')

			group = Group.objects.get(name='candidate')
			user.groups.add(group)

			messages.success(request, 'Account was created for ' + username)

			return redirect('login')
		

	context = {'form':form}
	return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
	jobs = Job.objects.all()
	candidates = Candidate.objects.all()

	total_Candidates = candidates.count()

	total_jobs = jobs.count()
	approved = jobs.filter(status='Approved').count()
	pending = jobs.filter(status='Pending').count()

	context = {'jobs':jobs, 'candidates':candidates,
	'total_jobs':total_jobs,'approved':approved,
	'pending':pending }

	return render(request, 'accounts/dashboard.html', context)

def userPage(request):
	context = {}
	return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
	products = Product.objects.all()

	return render(request, 'accounts/products.html', {'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def candidate(request, pk_test):
	candidate = Candidate.objects.get(id=pk_test)

	jobs = candidate.job_set.all()
	job_count = jobs.count()

	myFilter = OrderFilter(request.GET, queryset=jobs)
	jobs = myFilter.qs 

	context = {'candidate':candidate, 'jobs':jobs, 'job_count':job_count,
	'myFilter':myFilter}
	return render(request, 'accounts/customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createJob(request, pk):
	OrderFormSet = inlineformset_factory(Candidate, Job, fields=('product', 'status'), extra=10 )
	candidate = Candidate.objects.get(id=pk)
	formset = OrderFormSet(queryset=Job.objects.none(),instance=candidate)
	#form = OrderForm(initial={'Candidate':Candidate})
	if request.method == 'POST':
		#print('Printing POST:', request.POST)
		form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance=candidate)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'form':formset}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateJob(request, pk):

	order = Job.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteJob(request, pk):
	job = Job.objects.get(id=pk)
	if request.method == "POST":
		job.delete()
		return redirect('/')

	context = {'item':job}
	return render(request, 'accounts/delete.html', context)