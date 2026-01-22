from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Employee, AttendanceRecord
from datetime import date

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.name, 'Test User')
        self.assertTrue(self.user.check_password('testpass123'))


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            name='Admin'
        )
        self.employee = Employee.objects.create(
            employee_id='EMP001',
            full_name='John Doe',
            email='john@example.com',
            department='Engineering',
            created_by=self.user
        )

    def test_employee_creation(self):
        self.assertEqual(self.employee.employee_id, 'EMP001')
        self.assertEqual(self.employee.full_name, 'John Doe')
        self.assertEqual(self.employee.department, 'Engineering')

    def test_employee_unique_employee_id(self):
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_id='EMP001',  # Duplicate
                full_name='Jane Doe',
                email='jane@example.com',
                department='Design'
            )


class AttendanceRecordTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            name='Admin'
        )
        self.employee = Employee.objects.create(
            employee_id='EMP001',
            full_name='John Doe',
            email='john@example.com',
            department='Engineering'
        )

    def test_attendance_record_creation(self):
        attendance = AttendanceRecord.objects.create(
            employee=self.employee,
            date=date.today(),
            status='present',
            marked_by=self.user
        )
        self.assertEqual(attendance.employee, self.employee)
        self.assertEqual(attendance.status, 'present')

    def test_attendance_unique_constraint(self):
        AttendanceRecord.objects.create(
            employee=self.employee,
            date=date.today(),
            status='present'
        )
        with self.assertRaises(Exception):
            AttendanceRecord.objects.create(
                employee=self.employee,
                date=date.today(),  # Same employee, same date
                status='absent'
            )
