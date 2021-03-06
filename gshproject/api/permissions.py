from rest_framework import permissions
from manage.models import Domain
from node.models import Machine
class IsAuthenticatedOrCreate(permissions.IsAuthenticated):
	def has_permission(self, request, view):
		if request.method == 'POST':
			return True
		return super(IsAuthenticatedOrCreate, self).has_permission(request, view)
class DomainAuthenticate(object):
	def remove_space(self, string):
		return string.replace(" ", "").replace("\r\n", "").replace("\t", "")
	def has_permission(self, request, view):
		if request.method == 'POST':
			try:
				domain = Domain.objects.get(domain=request.data['domain'])
				machine = Machine.objects.get(id=str(request.data['id_machine']))
				if domain and domain.check_password(request.data['password']):
					if domain.filter_mode:
						if domain.filter_type:
							if machine.mac not in self.remove_space(domain.listmac).split(";"):
								return False
						else:
							if machine.mac in self.remove_space(domain.listmac).split(";"):
								return False
					request.domain = domain
					return True
			except Domain.DoesNotExist:
				return None
			except:
				return False
		return False