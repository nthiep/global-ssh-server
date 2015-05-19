import json, random, hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from api.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status
from api.permissions import IsAuthenticatedOrCreate, DomainAuthenticate
from oauth2_provider.models import AccessToken
from manage.models import Domain, Workgroup
from django.core.serializers.json import DjangoJSONEncoder

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_queryset(self):
        return [self.request.user]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate,)


class JoinDomain(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Domain.objects.all()
    serializer_class = JoinSerializer
    permission_classes = (DomainAuthenticate,)

    def get_queryset(self):
        return [self.request.domain]
    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
class AuthorizationView(APIView):
    def remove_space(self, string):
        return string.replace(" ", "").replace("\r\n", "").replace("\t", "")
    def post(self, request):
        id_machine = request.data["id_machine"]
        try:
            machine = Machine.objects.get(id=id_machine)
        except Machine.DoesNotExist:
            return Response({"status": "Machine Not Valid"}, status=status.HTTP_400_BAD_REQUEST)
        if request.auth:
            try:
                access = AccessToken.objects.get(token=request.auth)
            except AccessToken.DoesNotExist:                
                return Response({"status": "Token Denied"}, status=status.HTTP_400_BAD_REQUEST)
            if request.data["request"] == "authorization":
                if access.user.filter_mode:
                    if access.user.filter_type:
                        if machine.mac not in self.remove_space(access.user.listmac).split(";"):
                            return Response({"status": "Access Denied"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if machine.mac in self.remove_space(access.user.listmac).split(";"):
                            return Response({"status": "Access Denied"}, status=status.HTTP_400_BAD_REQUEST)
                machine.domain=access.user
            elif request.data["request"] == "logout":
                machine.domain=None
            else:                
                return Response({"status": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
            machine.workgroup= None
            machine.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)

        return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)

class MachineView(APIView):
    serializer_class = MachineSerializer

    def get(self, request):
        if request.auth:
            try:
                access = AccessToken.objects.get(token=request.auth)
            except AccessToken.DoesNotExist:
                return Response({"status": "access_token not accept!"}, status=status.HTTP_400_BAD_REQUEST)
            machine = Machine.objects.filter(domain=access.user, private=False)
            serializer = MachineSerializer(machine, many=True)
            return Response(serializer.data)
        return Response({"status": "request access denied!"}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        print request.data
        if "workgroup_id" in request.data:
            try:
                workgroup = Workgroup.objects.get(id=request.data["workgroup_id"],
                         secret_key=request.data["workgroup_secret"])
            except Workgroup.DoesNotExist:
                return Response({"status": "workgroup_id not accept"}, status=status.HTTP_400_BAD_REQUEST)
            machine = Machine.objects.filter(workgroup=workgroup, private=False)
            serializer = MachineSerializer(machine, many=True)
            return Response(serializer.data)
        return Response({"status": "request not accept!"}, status=status.HTTP_400_BAD_REQUEST)
def get_machine_domain(host=None, macpeer=None, domain=None):
    if macpeer:
        return Machine.objects.filter(mac=macpeer, domain=domain, private=False)
    elif host:
        return Machine.objects.filter(hostname=host, domain=domain, private=False)
    return False
def get_machine_workgroup(host=None, macpeer=None, workgroup=None):
    if macpeer:
        return Machine.objects.filter(mac=macpeer, workgroup=workgroup, private=False)
    elif host:
        return Machine.objects.filter(hostname=host, workgroup=workgroup, private=False)
    return False
@csrf_exempt
def MachineInfoView(request):
    print request.REQUEST
    if request.method == 'POST':
        if not request.REQUEST["join"]:
            machine = Machine.objects.filter(mac=request.REQUEST["mac"], private=False)
            if machine.count() == 1:
                machine = machine[0]
            else:
                return HttpResponse(json.dumps({"status": "Machine.DoesNotExist"}), status=400)
        elif request.REQUEST["join"] == "domain":
            try:
                access = AccessToken.objects.get(token=request.REQUEST["access_token"])
            except AccessToken.DoesNotExist:
                return HttpResponse(json.dumps({"status": "AccessToken.DoesNotExist"}), status=400)

            machine = get_machine_domain(request.REQUEST["host"], request.REQUEST["mac"], access.user)
            if machine and machine.count() > 0:
                machine=machine[0]
            else:
                return HttpResponse(json.dumps({"status": "Machine.DoesNotExist"}), status=400)
        elif request.REQUEST["join"] == "workgroup":
            try:
                workgroup = Workgroup.objects.get(id=request.REQUEST["workgroup_id"],
                    secret_key=request.REQUEST["workgroup_secret"])
                machine = get_machine_workgroup(request.REQUEST["host"], request.REQUEST["mac"], workgroup)
                if machine and machine.count() >0:
                    machine=machine[0]
                else:
                    return HttpResponse(json.dumps({"status": "Machine.DoesNotExist"}), status=400)

            except Workgroup.DoesNotExist:
                return HttpResponse(json.dumps({"status": "Workgroup.DoesNotExist"}), status=400)
        else:
            return HttpResponse(json.dumps({"status": "Machine.DoesNotExist"}), status=400)


        items_data = {}
        items_data['mac'] = machine.mac
        if machine.domain:
            items_data['join'] = "domain: " + machine.domain.domain
        elif machine.workgroup:
            if machine.workgroup.workgroup is not None:
                items_data['join'] = "workgroup: "+ machine.workgroup.workgroup
            else:
                items_data['join'] = "workgroup: "+ machine.workgroup.id
        else:
            items_data['join'] = "N/A"
        items_data['gateway'] = machine.gateway.ip
        items_data['nat'] = machine.nat
        items_data['nat_tcp'] = machine.nat_tcp
        items_data['added'] = machine.added
        items_data['hostname'] = machine.hostname
        items_data['platform'] = machine.platform
        items_data['ip'] = machine.ip
        items_json = json.dumps(items_data, cls=DjangoJSONEncoder)

        return HttpResponse(items_json, content_type="application/json")

def create_secretkey():
    """ create random secret key"""
    code = random.getrandbits(128)
    return hashlib.sha1(str(code)).hexdigest()
@csrf_exempt
def WorkgroupView(request):
    if request.method == 'POST':
        try:
            query = request.REQUEST["query"]
        except Exception as e:
            print e
            return HttpResponse(json.dumps({"status": "request not accept"}), status=400)
        if query == "CREATE":

            secret_key = create_secretkey()
            workgroup, created = Workgroup.objects.get_or_create(workgroup=request.REQUEST["workgroup"], 
                                secret_key = secret_key, mac_admin =  request.REQUEST["mac"])
            items_data = {}
            items_data['workgroup_id'] = workgroup.id
            items_data['workgroup'] = workgroup.workgroup
            items_data['workgroup_secret'] = workgroup.secret_key
            items_json = json.dumps(items_data, cls=DjangoJSONEncoder)

            return HttpResponse(items_json, content_type="application/json")
        elif query == "DELETE":
            try:
                workgroup = Workgroup.objects.get(id=request.REQUEST["workgroup_id"],
                    secret_key=request.REQUEST["workgroup_secret"], mac_admin = request.REQUEST["mac"])
            except Workgroup.DoesNotExist:
                return HttpResponse(json.dumps({"status": "not delete in server"}), status=400)

            workgroup.delete()
            return HttpResponse(json.dumps({"status": "success"}), status=200)

@csrf_exempt
def AuthWorkgroupView(request):
    if request.method == 'POST':
        try:
            id_machine = request.REQUEST["id_machine"]
            workgroup_id = request.REQUEST["workgroup_id"]
            workgroup_secret = request.REQUEST["workgroup_secret"]
            
        except:
            return HttpResponse(json.dumps({"status": "request not accept"}), status=400)

        try:
            machine = Machine.objects.get(id=id_machine)
        except Machine.DoesNotExist:
            return HttpResponse(json.dumps({"status": "Machine.DoesNotExist"}), status=400)
        try:
            workgroup = Workgroup.objects.get(id=workgroup_id, secret_key=workgroup_secret)
        except Workgroup.DoesNotExist:            
            return HttpResponse(json.dumps({"status": "error"}), status=400)
        try:
            if request.REQUEST["request"] == "JOIN":
                machine.workgroup=workgroup

            elif request.REQUEST["request"] == "LOGOUT":
                machine.workgroup=None
        except:
            return HttpResponse(json.dumps({"status": "bad request"}), status=400)

        machine.domain = None 
        machine.save()
        return HttpResponse(json.dumps({"status": "success"}), status=200)
@csrf_exempt
def NatconfigView(request):
    if request.method == 'POST':
        try:
            id_machine = request.REQUEST["id_machine"]
            nat = request.REQUEST["nat"]
            nat_tcp = request.REQUEST["nat_tcp"]
        except:
            return HttpResponse(json.dumps({"status": "request not accept"}), status=400)

        try:
            machine = Machine.objects.get(id=id_machine)
        except Machine.DoesNotExist:
            return HttpResponse(json.dumps({"status": "Machine.DoesNotExist"}), status=400)
        machine.nat=int(nat)
        machine.nat_tcp=int(nat_tcp)
        machine.save() 
        return HttpResponse(json.dumps({"status": "success"}), status=200)