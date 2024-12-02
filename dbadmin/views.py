from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

def transform_rent_type(code):
    mapping = {
        "available": "이용 가능",
        "long": "장기 대여",
        "short": "단기 대여",
        "unavailable": "사용 불가"
    }
    return mapping.get(code, code)

def reverse_transform_rent_type(korean):
    mapping = {
        "이용 가능": "available",
        "장기 대여": "long",
        "단기 대여": "short",
        "사용 불가": "unavailable"
    }
    return mapping.get(korean, korean)

def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt

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
            dict(zip(head, [transform_rent_type(row[2]) if col == '대여 여부' else row[i] for i, (col, value) in enumerate(zip(head, row))]))
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
                row[0],
                row[1],  # 이름
                row[2],  # 학번
                row[3],  # 학과(부)
                transform_rent_type(row[4]),  # 대여 구분 (이미 변환)
                format_datetime(row[5]),
                format_datetime(row[6])
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
                row[0],  # 이름
                row[1],  # 학번
                row[2],  # 학과(부)
                row[3],  # 사물함 번호
                format_datetime(row[4]),
                format_datetime(row[5])
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
@csrf_exempt
def update_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            if data['table_name'] == 'lockers':
                rental_state_mapping = {
                    '이용 가능': 'available',
                    '장기 대여': 'long',
                    '단기 대여': 'short',
                    '사용 불가': 'unavailable'
                }
                data['대여 여부'] = rental_state_mapping[data['대여 여부']]
                print(0)
                with connection.cursor() as cursor:
                    print(1)
                    cursor.execute(
                        "UPDATE lockers SET rental_state = %s WHERE locker_num = %s",
                        [data['대여 여부'], data['사물함 번호']]
                    )
                    print(2)
            elif data['table_name'] == 'rent':
                rental_state_mapping = {
                    '이용 가능': 'available',
                    '장기 대여': 'long',
                    '단기 대여': 'short',
                    '사용 불가': 'unavailable'
                }
                data['대여 구분'] = rental_state_mapping[data['대여 구분']]
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE rent SET student_id = %s, rent_type = %s, start_date = %s, end_date = %s WHERE locker_num = %s",
                        [data['학번'], data['대여 구분'], data['대여 시작 날짜'], data['대여 종료 날짜'], data['사물함 번호']]
                    )
            elif data['table_name'] == 'log':
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE log SET locker_num = %s, start_date = %s, end_date = %s WHERE student_id = %s",
                        [data['사물함 번호'], data['대여 시작 날짜'], data['대여 종료 날짜'], data['학번']]
                    )
            elif data['table_name'] =='student':
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE student SET name = %s, department = %s WHERE student_id = %s",
                        [data['이름'], data['학과(부)'], data['학번']]
                    )
            return JsonResponse({'success': True, 'message': '변경 사항이 적용되었습니다'})
        except Exception as e:  
            return JsonResponse({'success': False, 'message': '변경에 실패하였습니다. 다시 시도해 주세요.'})
    
        
    
