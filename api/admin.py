from django.contrib import admin
from .models import User, Employee, AttendanceRecord


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'role', 'department', 'is_active', 'joined_at']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['email', 'name']
    ordering = ['-joined_at']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'email', 'department', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['employee_id', 'full_name', 'email']
    ordering = ['-created_at']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'marked_by', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['employee__full_name', 'employee__employee_id']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
