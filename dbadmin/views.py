from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from django.db import connection
from datetime import datetime
import json

def dbadmin_login(request):
    error = None
    username = ""
    password = ""
    if request.method == "POST":
        username = request.POST.get('username', "")
        password = request.POST.get('password', "")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:  # 관리자만 접근 가능
                login(request, user)
                return redirect('dbadmin_home')
            else:
                error = "You are not authorized to access this page."
        else:
            error = "Invalid username or password."

    # 데이터베이스에서 B1 및 4F 데이터를 가져옵니다.
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM lockers WHERE TAG = 'B1' AND rental_state = 'available'")
        b1_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM lockers WHERE TAG = '4F' AND rental_state = 'available'")
        f4_count = cursor.fetchone()[0]

    return render(request, 'dbadmin/login.html', {
        'error': error,
        'username': username,
        'password': password,
        'b1_count': b1_count,
        'f4_count': f4_count,
    })

def dbadmin_logout(request):
    logout(request)
    return redirect('dbadmin_login')

@login_required(login_url='dbadmin_login')
def dbadmin_home(request):
    # DB 테이블 이름 가져오기
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
    return render(request, 'dbadmin/home.html')
   
@login_required(login_url='dbadmin_login')
def get_lockers_data(request):
    display_head = ('locker_num', 'TAG', 'rental_state')  # 실제 필드명 사용
    head = ('사물함 번호', '위치', '대여 여부')  # 프론트엔드에 표시할 이름
    with connection.cursor() as cursor:
        cursor.execute("SELECT locker_num, TAG, rental_state FROM lockers")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [
            dict(zip(head, [transform_rent_type(value) if col == '대여 여부' else value for col, value in zip(head, row)]))
            for row in result
        ]
    }

    return JsonResponse(data)

@login_required(login_url='dbadmin_login')
def get_rent_data(request):
    display_head = ('locker_num', 'name', 'student_id', 'department', 'rent_type', 'start_date', 'end_date')
    head = ('사물함 번호', '이름', '학번', '학과(부)', '대여 구분', '대여 시작 날짜', '대여 종료 날짜')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT locker_num, name, student_id, department, rent_type, start_date, end_date 
            FROM rent 
            NATURAL JOIN student 
            WHERE rent.student_id = student.student_id
        """)
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [
            dict(zip(head, [
                format_datetime(value) if col in ['대여 시작 날짜', '대여 종료 날짜'] else 
                transform_rent_type(value) if col == '대여 구분' else 
                value 
                for col, value in zip(head, row)
            ]))
            for row in result
        ]
    }

    return JsonResponse(data)

@login_required(login_url='dbadmin_login')
def get_log_data(request):
    display_head = ('name', 'student_id', 'department', 'locker_num', 'start_date', 'end_date')
    head = ('이름', '학번', '학과(부)', '사물함 번호', '대여 시작 날짜', '대여 종료 날짜')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name, student_id, department, locker_num, start_date, end_date 
            FROM log 
            NATURAL JOIN student 
            WHERE log.student_id = student.student_id
        """)
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [
            dict(zip(head, [
                format_datetime(value) if col in ['대여 시작 날짜', '대여 종료 날짜'] else 
                value 
                for col, value in zip(head, row)
            ]))
            for row in result
        ]
    }

    return JsonResponse(data)

@login_required(login_url='dbadmin_login')
def get_student_data(request):
    display_head = ('student_id', 'name', 'department')
    head = ('학번', '이름', '학과(부)')
    with connection.cursor() as cursor:
        cursor.execute("SELECT student_id, name, department FROM student")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [dict(zip(head, row)) for row in result]  # head와 데이터를 매핑
    }

    return JsonResponse(data)

@login_required(login_url='dbadmin_login')
def update_data(request, table_name):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    # 업데이트 가능한 테이블 목록
    allowed_tables = ['lockers', 'rent', 'log', 'student']
    if table_name not in allowed_tables:
        return JsonResponse({'success': False, 'error': 'Invalid table name'}, status=400)
    
    # 각 테이블의 기본 키 설정
    primary_keys = {
        'lockers': 'locker_num',
        'rent': 'id',      # 실제 기본 키 필드명으로 변경 필요
        'log': 'id',       # 실제 기본 키 필드명으로 변경 필요
        'student': 'student_id',
    }
    
    pk_field = primary_keys.get(table_name)
    if not pk_field:
        return JsonResponse({'success': False, 'error': 'Primary key not defined for table'}, status=400)
    
    pk = data.get('pk')
    if not pk:
        return JsonResponse({'success': False, 'error': 'Primary key not provided'}, status=400)
    
    # 'rental_state' 값 변환 (한글 -> 코드)
    if table_name == 'lockers' and 'rental_state' in data:
        rental_state_mapping = {
            "이용 가능": "available",
            "장기 대여": "long",
            "단기 대여": "short",
            "사용 불가": "unavailable"
        }
        data['rental_state'] = rental_state_mapping.get(data['rental_state'], data['rental_state'])
    
    # SET 절 생성
    set_fields = []
    values = []
    for key, value in data.items():
        if key == 'pk':
            continue
        set_fields.append(f"{key} = %s")
        values.append(value)
    
    if not set_fields:
        return JsonResponse({'success': False, 'error': 'No fields to update'}, status=400)
    
    set_clause = ", ".join(set_fields)
    values.append(pk)  # WHERE 절을 위한 값 추가
    
    # UPDATE 쿼리 실행
    try:
        with connection.cursor() as cursor:
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {pk_field} = %s"
            cursor.execute(sql, values)
        return JsonResponse({'success': True})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': 'Database update failed'}, status=500)

 # 대여 구분 변환 함수
def transform_rent_type(rent_type):
    mapping = {
        "available": "이용 가능",
        "long": "장기 대여",
        "short": "단기 대여",
        "unavailable": "사용 불가"
    }
    return mapping.get(rent_type, rent_type)

def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt