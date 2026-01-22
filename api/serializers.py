from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Employee, AttendanceRecord


class UserSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'phone', 'department', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'phone', 'department']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
            department=validated_data.get('department', ''),
            role='HR Manager'
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password"')

        return data


class EmployeeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_employee_id(self, value):
        # Check if employee_id is unique
        employee_id = self.initial_data.get('employee_id') or self.initial_data.get('employeeId')
        if employee_id:
            if self.instance:
                # Update: exclude current instance
                if Employee.objects.exclude(pk=self.instance.pk).filter(employee_id=employee_id).exists():
                    raise serializers.ValidationError('Employee ID already exists')
            else:
                # Create: check if exists
                if Employee.objects.filter(employee_id=employee_id).exists():
                    raise serializers.ValidationError('Employee ID already exists')
        return value

    def validate_email(self, value):
        # Check if email is unique
        if self.instance:
            # Update: exclude current instance
            if Employee.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError('Email already exists')
        else:
            # Create: check if exists
            if Employee.objects.filter(email=value).exists():
                raise serializers.ValidationError('Email already exists')
        return value


class AttendanceRecordSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    employee_id = serializers.CharField(source='employee.id', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'employee_id', 'date', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'employee_id']


class MarkAttendanceSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    date = serializers.DateField()
    status = serializers.ChoiceField(choices=['present', 'absent'])

    def validate_employee_id(self, value):
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError('Employee does not exist')
        return value


class AttendanceStatsSerializer(serializers.Serializer):
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    total = serializers.IntegerField()
