from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Employee, AttendanceRecord
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create admin user if not exists
        if not User.objects.filter(email='admin@hrms.com').exists():
            admin = User.objects.create_user(
                email='admin@hrms.com',
                password='admin123',
                name='Admin User',
                role='Administrator',
                department='Management'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin user: {admin.email}'))
        else:
            admin = User.objects.get(email='admin@hrms.com')
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Sample employees data
        employees_data = [
            {
                'employee_id': 'EMP001',
                'full_name': 'John Doe',
                'email': 'john.doe@company.com',
                'department': 'Engineering'
            },
            {
                'employee_id': 'EMP002',
                'full_name': 'Jane Smith',
                'email': 'jane.smith@company.com',
                'department': 'Design'
            },
            {
                'employee_id': 'EMP003',
                'full_name': 'Mike Johnson',
                'email': 'mike.johnson@company.com',
                'department': 'Marketing'
            },
            {
                'employee_id': 'EMP004',
                'full_name': 'Sarah Williams',
                'email': 'sarah.williams@company.com',
                'department': 'Sales'
            },
            {
                'employee_id': 'EMP005',
                'full_name': 'David Brown',
                'email': 'david.brown@company.com',
                'department': 'HR'
            },
            {
                'employee_id': 'EMP006',
                'full_name': 'Emily Davis',
                'email': 'emily.davis@company.com',
                'department': 'Finance'
            },
            {
                'employee_id': 'EMP007',
                'full_name': 'Robert Miller',
                'email': 'robert.miller@company.com',
                'department': 'Operations'
            },
            {
                'employee_id': 'EMP008',
                'full_name': 'Lisa Anderson',
                'email': 'lisa.anderson@company.com',
                'department': 'Engineering'
            },
        ]

        # Create employees
        created_employees = []
        for emp_data in employees_data:
            employee, created = Employee.objects.get_or_create(
                employee_id=emp_data['employee_id'],
                defaults={
                    'full_name': emp_data['full_name'],
                    'email': emp_data['email'],
                    'department': emp_data['department'],
                    'created_by': admin
                }
            )
            if created:
                created_employees.append(employee)
                self.stdout.write(self.style.SUCCESS(f'✓ Created employee: {employee.full_name}'))
            else:
                created_employees.append(employee)
                self.stdout.write(self.style.WARNING(f'Employee already exists: {employee.full_name}'))

        # Create attendance records for the last 7 days
        if created_employees:
            self.stdout.write('\nCreating attendance records...')
            today = date.today()
            
            for i in range(7):
                attendance_date = today - timedelta(days=i)
                
                for employee in created_employees:
                    # Random attendance status (90% present, 10% absent)
                    status = 'present' if random.random() < 0.9 else 'absent'
                    
                    attendance, created = AttendanceRecord.objects.get_or_create(
                        employee=employee,
                        date=attendance_date,
                        defaults={
                            'status': status,
                            'marked_by': admin
                        }
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Marked {employee.full_name} as {status} on {attendance_date}'
                            )
                        )

        self.stdout.write(self.style.SUCCESS('\n✓ Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now login with:'))
        self.stdout.write(self.style.SUCCESS('  Email: admin@hrms.com'))
        self.stdout.write(self.style.SUCCESS('  Password: admin123'))
