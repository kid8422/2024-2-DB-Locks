# main/views.py

import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 대한민국 시간대 설정
kst = ZoneInfo('Asia/Seoul')

def login_view(request):
    """
    로그인 페이지를 렌더링합니다.
    SSO 로그인 성공 후 sToken과 sIdno를 쿼리 파라미터로 받습니다.
    """
    sToken = request.GET.get('sToken')
    sIdno = request.GET.get('sIdno')
    login_status = request.GET.get('login_status', '')  # 로그인 상태를 추가로 받기

    with connection.cursor() as cursor:
        # B1의 rental_state가 1인 사물함 수 카운트
        cursor.execute("SELECT COUNT(*) FROM lockers WHERE TAG = 'B1' AND rental_state = 'available'")
        b1_count = cursor.fetchone()[0]

        # 4F의 rental_state가 1인 사물함 수 카운트
        cursor.execute("SELECT COUNT(*) FROM lockers WHERE TAG = '4F' AND rental_state = 'available'")
        f4_count = cursor.fetchone()[0]

    return render(request, 'main/login.html', {'sToken': sToken, 'sIdno': sIdno, 'login_status': login_status, 'b1_count': b1_count, 'f4_count': f4_count})

def login_redirect(request):
    """
    SSO 로그인 페이지로 리다이렉트합니다.
    """
    callback_url = request.build_absolute_uri(reverse('callback'))
    login_url = f"https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl={callback_url}"
    return redirect(login_url)

def callback_view(request):
    """
    SSO 로그인 성공 후 리다이렉트되는 콜백 뷰입니다.
    sToken과 sIdno를 받아서 로그인 페이지로 전달합니다.
    """
    sToken = request.GET.get('sToken')
    sIdno = request.GET.get('sIdno')

    if not sToken or not sIdno:
        # 토큰이 없으면 로그인 실패로 간주하고 로그인 페이지로 리디렉션
        return redirect(f"{reverse('login')}?login_status=fail")

    # 로그인 페이지로 리디렉트하면서 토큰을 전달 (쿼리 파라미터로)
    return redirect(f"{reverse('login')}?sToken={sToken}&sIdno={sIdno}")

def fetch_user_info(sToken, sIdno):
    """
    SSO 서버에서 사용자 정보를 동기적으로 가져옵니다.
    """
    try:
        sapTokenUrl = f"https://saint.ssu.ac.kr/webSSO/sso.jsp?sToken={sToken}"
        mainStudentUrl = "https://saint.ssu.ac.kr/webSSUMain/main_student.jsp"

        headers = {"Cookie": f"sToken={sToken}"}

        with requests.Session() as session:
            session.get(sapTokenUrl, headers=headers)
            response = session.get(mainStudentUrl)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch user info. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None

def parse_user_info(html_text):
    """
    SSO 서버의 HTML 응답에서 사용자 정보를 파싱합니다.
    """
    try:
        soup = BeautifulSoup(html_text, 'lxml')  # HTML 문자열을 BeautifulSoup 객체로 파싱

        # 이름 추출
        welcome_p = soup.find('p', class_='main_title')
        name = welcome_p.text.strip().replace("님 환영합니다.", "") if welcome_p else "알 수 없음"

        # 학번 및 소속 추출
        student_id = "알 수 없음"
        department = "알 수 없음"
        is_enrolled = False  # 초기값 설정

        dt_tags = soup.find_all('dt')
        for dt in dt_tags:
            if dt.text.strip() == '학번':
                dd = dt.find_next_sibling('dd')
                if dd and dd.find('strong'):
                    student_id = dd.find('strong').text.strip()
            elif dt.text.strip() == '소속':
                dd = dt.find_next_sibling('dd')
                if dd and dd.find('strong'):
                    department = dd.find('strong').text.strip()
            elif dt.text.strip() == '과정/학기':  # 재학 여부에 대한 태그가 있다고 가정
                dd = dt.find_next_sibling('dd')
                if dd and dd.find('strong'):
                    status_text = dd.find('strong').text.strip()
                    is_enrolled = status_text

        #print(name, student_id, department, is_enrolled)

        return {
            'name': name,
            'student_id': student_id,
            'department': department,
            'is_enrolled': is_enrolled,
        }
    except Exception as e:
        print(f"Error parsing user info: {e}")
        return None

@csrf_exempt
def get_user_info(request):
    """
    클라이언트로부터 sToken과 sIdno를 받아 사용자 정보를 반환합니다.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'GET method is not supported. Use POST instead.'}, status=405)

    try:
        data = json.loads(request.body)
        sToken = data.get('sToken')
        sIdno = data.get('sIdno')

        if not sToken or not sIdno:
            return JsonResponse({'error': 'Missing sToken or sIdno.'}, status=400)

        html_response = fetch_user_info(sToken, sIdno)
        if not html_response:
            return JsonResponse({'error': 'Failed to fetch user info from SSO.'}, status=500)

        user_info = parse_user_info(html_response)

        if user_info:
            # 학부 및 재학 여부 확인
            if user_info['department'] != 'AI융합학부':
                return JsonResponse({'success': False, 'error': 'InvalidDepartment'}, status=200)
            if not user_info['is_enrolled']:
                return JsonResponse({'success': False, 'error': 'NotEnrolled'}, status=200)

            # 세션에 사용자 정보 저장
            request.session['user_info'] = user_info
            return JsonResponse({'success': True, 'user_info': user_info})
        else:
            return JsonResponse({'error': 'Failed to parse user info.'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

def reservation_view(request):
    """
    예약 페이지를 렌더링합니다.
    사용자 정보가 세션에 없으면 로그인 페이지로 리디렉션합니다.
    """
    user_info = request.session.get('user_info')
    if not user_info:
        return redirect('login')

    # 사물함 데이터 예시 (실제 데이터는 데이터베이스나 API에서 불러올 수 있습니다)
    lockers = [
        {'id': i + 21, 'status': 'reserved' if i % 7 == 0 else 'available', 'zone': 'A 구역'}
        for i in range(70)
    ]

    return render(request, 'main/reservation.html', {'user_info': user_info, 'lockers': lockers})

def load_4F_lockers(request):
    head = ('사물함 번호', '대여 구분')
    with connection.cursor() as cursor:
        cursor.execute("select locker_num, rental_state from lockers WHERE TAG = '4F'")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [dict(zip(head, row)) for row in result]
    }

    return JsonResponse(data)

def load_B1_lockers(request):
    head = ('사물함 번호', '대여 구분')
    with connection.cursor() as cursor:
        cursor.execute("select locker_num, rental_state from lockers WHERE TAG = 'B1'")
        result = cursor.fetchall()
    
    # 데이터를 JSON으로 변환
    data = {
        "head": head,
        "rows": [dict(zip(head, row)) for row in result]
    }

    return JsonResponse(data)
    
@csrf_exempt
def return_locker(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data['student_id']
            locker_num = data['locker_num']
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT start_date FROM rent WHERE student_id = %s",
                    [student_id]
                )
                start_date = cursor.fetchone()[0]

                current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

                # 2-1) lockers 테이블에서 상태 변경
                cursor.execute(
                    "UPDATE lockers SET rental_state = 'available' WHERE locker_num = %s",
                    [locker_num]
                )

                # 2-2) log 테이블에 반납 기록 추가
                cursor.execute(
                    "INSERT INTO log (student_id, locker_num, start_date, end_date) VALUES (%s, %s, %s, %s)",
                    [student_id, locker_num, start_date, current_time]
                )

                # 2-4) rent 테이블에서 데이터 삭제
                cursor.execute(
                    "DELETE FROM rent WHERE student_id = %s AND locker_num = %s",
                    [student_id, locker_num]
                )
            return JsonResponse({"success": True, "message": "Locker returned successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
    
@shared_task
def auto_return_locks():
    try:
        with connection.cursor() as cursor:
            # 현재 시간 이전에 만료된 사물함 찾기
            cursor.execute(
                "SELECT locker_num, student_id FROM rent WHERE rental_date < %s",
                [(datetime.now(kst) - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')]
            )
            expired_rentals = cursor.fetchall()

            for locker_num, student_id in expired_rentals:
                # lockers 테이블 상태 변경
                cursor.execute(
                    "UPDATE lockers SET rental_state = 'available' WHERE locker_num = %s",
                    [locker_num]
                )

                # log 테이블에 자동 반납 기록 추가
                cursor.execute(
                    "INSERT INTO log (student_id, locker_num, action, action_time) VALUES (%s, %s, 'auto-returned', %s)",
                    [student_id, locker_num, datetime.now(kst).strftime('%Y-%m-%d %H:%M')]
                )

                # student 및 rent 테이블에서 데이터 삭제
                cursor.execute("DELETE FROM student WHERE student_id = %s", [student_id])
                cursor.execute("DELETE FROM rent WHERE student_id = %s AND locker_num = %s", [student_id, locker_num])

        return "Auto return process completed."

    except Exception as e:
        return f"Error in auto-return process: {str(e)}"
    
@csrf_exempt
def reserve_locker(request):
    if request.method == 'POST':
        try:
            # 클라이언트에서 데이터 수신
            data = json.loads(request.body)
            locker_num = data['locker_num']
            student_id = data['student_id']
            student_name = data['student_name']
            student_department = data['student_department']
            current_date = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
            future_date = (datetime.now(kst) + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
            print(locker_num, student_id, current_date, future_date)

            # 데이터베이스 업데이트
            with connection.cursor() as cursor:
                # 대여 가능 여부 확인
                print(1)
                cursor.execute(
                    "SELECT COUNT(*) FROM rent WHERE student_id = %s",
                    [student_id]
                )
                result = cursor.fetchone()[0]
                print("result :", result)
                if result != 0:
                    return JsonResponse({'success': False, 'message': '대여 중인 사물함이 있습니다.'})

                # studnet 테이블 추가
                print(2)
                cursor.execute(
                    "SELECT COUNT(*) FROM student WHERE student_id = %s",
                    [student_id]
                )
                count = cursor.fetchone()[0]
                if (count == 0):
                    cursor.execute(
                        "INSERT INTO student (student_id, name, department) VALUES (%s, %s, %s)",
                        [student_id, student_name, student_department]
                    )

                # rent 테이블 추가
                print(3)
                cursor.execute(
                    "INSERT INTO rent (locker_num, student_id, rent_type, start_date, end_date) VALUES (%s, %s, 'short', %s, %s)",
                    [locker_num, student_id, current_date, future_date]
                )

                print(5)
                # lockers 테이블 업데이트
                cursor.execute(
                    "UPDATE lockers SET rental_state = 'short' WHERE locker_num = %s",
                    [locker_num]
                )
                print(6)

            return JsonResponse({'success': True, 'message': f'{locker_num}번 사물함이 예약되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# STUDENT_ID를 이용해 rent 테이블에서 예약 정보를 가져옵니다.
@csrf_exempt
def get_myreservation_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data['student_id']
            with connection.cursor() as cursor:
                # rent 테이블에서 학생의 예약 정보를 검색
                cursor.execute("SELECT locker_num, start_date, end_date FROM rent WHERE student_id = %s",
                    [student_id]
                )
                result = cursor.fetchone()
                start_date = result[1].strftime('%Y-%m-%d %H:%M')
                end_date = result[2].strftime('%Y-%m-%d %H:%M')

                cursor.execute("SELECT TAG FROM lockers WHERE locker_num = %s",
                    [result[0]]
                )
                tag = cursor.fetchone()[0]
                print(tag, result[0], start_date, end_date)
            return JsonResponse({'success': True, 'data': {
                'floor': tag,
                'locker_num': result[0],
                'start_date': start_date,
                'end_date': end_date
            }})
        except Exception as e:
            print('error')
            return JsonResponse({'success': False, 'data': str(e)})