from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from datetime import datetime, date
from .models import User, Employee, AttendanceRecord
from .serializers import (
    UserSerializer,
    SignupSerializer,
    LoginSerializer,
    EmployeeSerializer,
    AttendanceRecordSerializer,
    MarkAttendanceSerializer,
    AttendanceStatsSerializer
)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Register a new user"""
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update user profile"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Employee ViewSet
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employees
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Employee.objects.all()
        
        # Filter by department
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)
        
        # Search by name or employee_id or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def check_unique(self, request):
        """Check if employee_id or email is unique"""
        employee_id = request.query_params.get('employee_id', None)
        email = request.query_params.get('email', None)
        
        result = {}
        
        if employee_id:
            result['employee_id_unique'] = not Employee.objects.filter(employee_id=employee_id).exists()
        
        if email:
            result['email_unique'] = not Employee.objects.filter(email=email).exists()
        
        return Response(result)


# Attendance ViewSet
class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance records
    """
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related('employee').all()
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id', None)
        if employee_id:
            queryset = queryset.filter(employee__id=employee_id)
        
        # Filter by date
        date_param = self.request.query_params.get('date', None)
        if date_param:
            queryset = queryset.filter(date=date_param)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        return queryset

    @action(detail=False, methods=['post'])
    def mark(self, request):
        """Mark attendance for an employee"""
        serializer = MarkAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            employee_id = serializer.validated_data['employee_id']
            date_value = serializer.validated_data['date']
            status_value = serializer.validated_data['status']
            
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Update or create attendance record
            attendance, created = AttendanceRecord.objects.update_or_create(
                employee=employee,
                date=date_value,
                defaults={
                    'status': status_value,
                    'marked_by': request.user
                }
            )
            
            result_serializer = AttendanceRecordSerializer(attendance)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def today_stats(self, request):
        """Get today's attendance statistics"""
        today = date.today()
        today_records = AttendanceRecord.objects.filter(date=today)
        
        stats = {
            'present': today_records.filter(status='present').count(),
            'absent': today_records.filter(status='absent').count(),
            'total': today_records.count(),
        }
        
        serializer = AttendanceStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get attendance records for a specific employee"""
        employee_id = request.query_params.get('employee_id', None)
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        records = AttendanceRecord.objects.filter(employee=employee).order_by('-date')
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Get attendance records for a specific date"""
        date_param = request.query_params.get('date', None)
        if not date_param:
            return Response({'error': 'date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        records = AttendanceRecord.objects.filter(date=date_param).select_related('employee')
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)


# Dashboard Stats View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    total_employees = Employee.objects.count()
    
    today = date.today()
    today_attendance = AttendanceRecord.objects.filter(date=today)
    present_today = today_attendance.filter(status='present').count()
    absent_today = today_attendance.filter(status='absent').count()
    
    return Response({
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'attendance_marked': today_attendance.count(),
    })
