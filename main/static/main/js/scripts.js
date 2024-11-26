function startLogin() {
    // "로그인 중" 메시지 표시
    document.getElementById('content').innerHTML = `
        <p class="text-blue-500 font-semibold">로그인 중...</p>
    `;

    // 로그인 페이지로 리디렉트
    window.location.href = LOGIN_REDIRECT_URL;
}

// 페이지 로드 시 쿼리 파라미터에서 sToken과 sIdno 가져오기
window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const sToken = urlParams.get('sToken');
    const sIdno = urlParams.get('sIdno');

    if (sToken && sIdno) {
        // "로그인 중..." 메시지와 함께 사용자 정보 요청
        document.getElementById('content').innerHTML = `
            <p class="text-blue-500 font-semibold">로그인 중...</p>
        `;

        // AJAX 요청을 통해 사용자 정보 가져오기
        fetch(GET_USER_INFO, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')  // CSRF 토큰
            },
            body: JSON.stringify({
                "sToken": sToken,
                "sIdno": sIdno
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const userInfo = data.user_info;
                // 사용자 정보 표시
                document.getElementById('content').innerHTML = `
                    <p class="text-blue-500 font-semibold">로그인 중...</p>
                    <div class="mt-4">
                        <h2 class="text-xl font-semibold">내 정보</h2>
                        <p>이름: ${userInfo.name}</p>
                        <p>학번: ${userInfo.student_id}</p>
                        <p>소속: ${userInfo.department}</p>
                    </div>
                `;

                // 2초 후 예약 페이지로 리디렉션
                setTimeout(function() {
                    window.location.href = RESERVATION;
                }, 2000);
            } else {
                // 에러 메시지 표시
                document.getElementById('content').innerHTML = `
                    <p class="text-red-500 font-semibold">로그인 실패. 다시 시도해주세요.</p>
                    <button onclick="startLogin()" class="bg-blue-500 text-white py-2 px-4 rounded mt-4">통합 로그인</button>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('content').innerHTML = `
                <p class="text-red-500 font-semibold">로그인 과정에서 오류가 발생했습니다.</p>
                <button onclick="startLogin()" class="bg-blue-500 text-white py-2 px-4 rounded mt-4">통합 로그인</button>
            `;
        });
    }
}

// CSRF 토큰 가져오기 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // 쿠키가 name으로 시작하는지 확인
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}