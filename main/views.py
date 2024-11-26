# main/views.py

import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup

def login_view(request):
    """
    로그인 페이지를 렌더링합니다.
    SSO 로그인 성공 후 sToken과 sIdno를 쿼리 파라미터로 받습니다.
    """
    sToken = request.GET.get('sToken')
    sIdno = request.GET.get('sIdno')
    return render(request, 'main/login.html', {'sToken': sToken, 'sIdno': sIdno})

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
        return redirect('login')

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
                    
        return {
            'name': name,
            'student_id': student_id,
            'department': department,
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
