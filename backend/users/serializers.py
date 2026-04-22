from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required= True, validators=[validate_password])
    password = serializers.CharField(write_only = True, requires = True, label = 'Confirm password')

    class Meta:
        model = User
        feilds = ('email', 'first_name', 'last_name', 'password', 'password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': "passwords do not match."})
        return attrs
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        feilds = ('id', 'email', 'first_name', 'last_name', 'full_name', 'date_joined')
        read_only_feilds = ('id', 'date_joined')
