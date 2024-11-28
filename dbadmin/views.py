from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from django.db import connection

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
    head = ('사물함 번호', '위치', '대여 여부')
    with connection.cursor() as cursor:
        cursor.execute("select * from lockers")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
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
    head = ('사물함 번호', '대여자 학번', '대여 구분', '대여 날짜', '대여 기간')
    with connection.cursor() as cursor:
        cursor.execute("select * from rent")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [
            dict(zip(head, [transform_rent_type(value) if col == '대여 구분' else value for col, value in zip(head, row)]))
            for row in result
        ]
    }

    return JsonResponse(data)

@login_required(login_url='dbadmin_login')
def get_log_data(request):
    head = ('대여자 학번', '대여 날짜', '대여 기간')
    with connection.cursor() as cursor:
        cursor.execute("select * from log")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [dict(zip(head, row)) for row in result]  # head와 데이터를 매핑
    }

    return JsonResponse(data)

@login_required(login_url='dbadmin_login')
def get_student_data(request):
    head = ('학번', '이름', '학과(부)')
    with connection.cursor() as cursor:
        cursor.execute("select * from student")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [dict(zip(head, row)) for row in result]  # head와 데이터를 매핑
    }

    return JsonResponse(data)

 # 대여 구분 변환 함수
def transform_rent_type(rent_type):
    if rent_type == "long":
        return "장기 대여"
    elif rent_type == "short":
        return "단기 대여"
    elif rent_type == "available":
        return "이용 가능"
    return rent_type  # 변환되지 않은 값은 그대로 반환