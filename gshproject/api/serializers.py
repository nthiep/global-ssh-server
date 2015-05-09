from django.contrib.auth.models import User, Group
from manage.models import Application
from rest_framework import serializers
from node.models import *
from manage.models import Domain

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class SignUpSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()
    domain = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'password', 'client_id', 'client_secret', 'domain')
        write_only_fields = ('password',)

    def domain_obj(self, obj):
        return Domain.objects.get(user=obj.id, domain="root."+obj.username)
    def get_domain(self, obj):
        return self.domain_obj(obj).domain
    def get_client_id(self, obj):

        return Application.objects.get(user=self.domain_obj(obj).id, domain=self.domain_obj(obj).id).client_id

    def get_client_secret(self, obj):
        return Application.objects.get(user=self.domain_obj(obj).id, domain=self.domain_obj(obj).id).client_secret

class JoinSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = Domain
        fields = ('domain', 'client_id', 'client_secret')

    def get_client_id(self, obj):
        return Application.objects.get(domain=obj.id).client_id

    def get_client_secret(self, obj):
        return Application.objects.get(domain=obj.id).client_secret

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ('mac', 'hostname', 'platform', 'ip')
        