from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from manage.models import Domain, Workgroup
from node.models import Machine, Gateway
from pages.forms import DomainFormView, DomainFormCreate, DomainFormDelete
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
def index(request):
	# Create a response
	response =  render_to_response('pages/home.html', RequestContext(request))
	# Return the response
	return response

def register(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			return HttpResponseRedirect('/login/?redirect=register')
	else:
		form = UserCreationForm()
	return render(request, "pages/register.html", {
		'form': form,
	})


def user_login(request):
	# Like before, obtain the context for the user's request.
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	error = False
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password']

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/dashboard/')
			else:
				# An inactive account was used - no logging in!
				error = "access denied!"
		else:
			# Bad login details were provided. So we can't log the user in.
			error = "Invalid login details supplied."

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	redirect = False
	if 'redirect' in request.GET:
		redirect = True
	context = RequestContext(request)
	return render_to_response('pages/login.html', {'error': error, 'redirect': redirect}, context)

@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/')

@login_required
def Dashboard(request):
	context = RequestContext(request)
	domain = Domain.objects.filter(user=request.user)
	machine = 0
	gateway = 0
	for d in domain:
		machine_list = Machine.objects.filter(domain=d)
		machine += machine_list.count()
		ls =[]
		for l in machine_list:
			if l.gateway:
				if l.gateway not in ls:
					ls.append(l.gateway)
					gateway +=1

	return render_to_response('pages/dashboard.html',
		 {'page': 'Dashboard', 'domain': domain.count(), 'machine': machine,
		 'gateway': gateway, 'domain_list': domain}, context)
@login_required
def DomainView(request):
	context = RequestContext(request)
	try:
		user = User.objects.get(username=request.user)
	except User.DoesNotExist:
		return HttpResponseRedirect('/dashboard/')
	domain = Domain.objects.filter(user=user)

	return render_to_response('pages/domain.html', {'page': 'Domain', 'data': domain, 'domain_list': domain}, context)
@login_required
def DomainEditView(request, domain = None):
	d = None
	delete = False
	if domain is not None:
		try:
			d = Domain.objects.get(domain=domain, user=request.user)
			delete = "/domain/delete/%s/" %domain
		except Domain.DoesNotExist:
			return HttpResponseRedirect('/domain/')
	if request.method == 'POST':
		if domain is not None:			
			form = DomainFormView(request.POST, instance=d)
		else:
			mutable = request.POST._mutable
			request.POST._mutable = True
			request.POST['domain'] = "%s.%s" %(request.POST["domain"], request.user)
			request.POST._mutable = mutable
			form = DomainFormCreate(request.POST, instance=d)
			user = User.objects.get(username=request.user)

		if form.is_valid():
			if domain is not None:
				m = form.save()
				if request.POST["new_password"] and d.check_password(request.POST["old_password"]):
					m.set_password(request.POST["new_password"])
					m.save()
			else:
				m = form.save(user=user)
				m.set_password(request.POST["password"])
				m.save()

			return HttpResponseRedirect('/domain/')
	else:
		if domain is None:
			form = DomainFormCreate(instance = d)
		else:
			form = DomainFormView(instance=d)
	# Either the form was not valid, or we've just created it
	if domain is not None:
		page = "Edit Domain %s" %domain
	else:
		page = "Create New Domain"
	domain_list = Domain.objects.filter(user=request.user)
	f = {'form': form, 'delete': delete, 'page': page, 'domain_list': domain_list}
	if domain:
		# The template needs the id to decide if the form's action
		# is .../add_task or .../{{id}}/edit
		f['domain'] = d.domain
	return render_to_response('pages/editdomain.html', f,
		context_instance=RequestContext(request))

@login_required
def DomainDeleteView(request, domain=None):
	try:
		d = Domain.objects.get(domain=domain, user=request.user)
		machine = Machine.objects.filter(domain=d)
	except Domain.DoesNotExist:
		return HttpResponseRedirect('/domain/')
	if request.method == 'POST':
		form = DomainFormDelete(request.POST, instance=d)

		if form.is_valid(): # checks CSRF
			d.delete()
			return HttpResponseRedirect("/domain/")
	else:
		form = DomainFormDelete(instance=d)
	domain_list = Domain.objects.filter(user=request.user)
	f = {'form': form, 'page': "Delete domain %s" %d.domain,
		'machine': machine, 'domain_list': domain_list}
	return render_to_response('pages/deletedomain.html', f,
		context_instance=RequestContext(request))

@login_required
def MachineView(request, domain=None):
	context = RequestContext(request)
	if domain is not None:
		try:
			d = Domain.objects.get(domain=domain, user=request.user)

		except Domain.DoesNotExist:
			return HttpResponseRedirect('/dashboard/')
	else:
		d = Domain.objects.filter(user=request.user)
		if d.count() ==0:
			return HttpResponseRedirect('/dashboard/')
		d = d[0]
	domain_user		= Domain.objects.filter(user=request.user)
	machine = Machine.objects.filter(domain=d)
	return render_to_response('pages/machine.html',
		 {'page': 'Machine of %s' %d.domain, 'data': machine,
		  'domain': domain_user, 'domain_list': domain_user}, context)
@login_required
def GatewayView(request, domain=None):
	context = RequestContext(request)
	if domain is not None:
		try:
			d = Domain.objects.get(domain=domain, user=request.user)
		except Domain.DoesNotExist:
			return HttpResponseRedirect('/dashboard/')
	else:
		d = Domain.objects.filter(user=request.user)
		if d.count() ==0:
			return HttpResponseRedirect('/dashboard/')
		d = d[0]
	machine = Machine.objects.filter(domain=d)
	ls = []
	for m in machine:
		if m.gateway and m.gateway not in ls:
			ls.append(m.gateway)
	domain_obj = Domain.objects.filter(user=request.user)

	return render_to_response('pages/gateway.html', {'page': 'Gateway of %s' %d.domain,
	 'data': ls, 'domain_list': domain_obj}, context)
@login_required
def GatewayDetailView(request, gateway):
	context = RequestContext(request)
	try:
		g = Gateway.objects.get(id=gateway)
	except:
		return HttpResponseRedirect('/dashboard/')
	domain_obj = Domain.objects.filter(user=request.user)

	from django.contrib.gis.utils import GeoIP
	g = GeoIP()
	city = g.city(g.ip)['city']
	country = g.city(g.ip)['country']
	return render_to_response('pages/gatewayview.html', {'page': 'Gateway %s' %g.ip,
	 'data': g, 'city': city, 'country': country, 'domain_list': domain_obj}, context)
@login_required
def NetmapView(request, domain=None):
	context = RequestContext(request)
	if domain is not None:
		try:
			d = Domain.objects.get(domain=domain, user=request.user)
		except Domain.DoesNotExist:
			return HttpResponseRedirect('/dashboard/')
	else:
		d = Domain.objects.filter(user=request.user)
		if d.count() ==0:
			return HttpResponseRedirect('/dashboard/')
		d = d[0]
	domain_obj = Domain.objects.filter(user=request.user)

	return render_to_response('pages/netmap.html', {'page': 'Network Map of %s' %d.domain,
	 'data': domain_obj, 'domain_list': domain_obj}, context)

def handler404(request):
	response = render_to_response('pages/404.html', {},
                                  context_instance=RequestContext(request))
	response.status_code = 404
	return response
def handler500(request):
	response = render_to_response('pages/404.html', {},
                                  context_instance=RequestContext(request))
	response.status_code = 500
	return response

def about(request):
	return HttpResponseRedirect("https://gssh.github.io/about.html")
