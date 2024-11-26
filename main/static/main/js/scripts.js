function startLogin() {
    // 로그인 페이지로 리디렉트
    window.location.href = LOGIN_REDIRECT_URL;

}

// 페이지 로드 시 쿼리 파라미터에서 sToken과 sIdno 가져오기
window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const sToken = urlParams.get('sToken');
    const sIdno = urlParams.get('sIdno');

    if (sToken && sIdno) {
        const loginButton = document.getElementById('login-button');

        // 버튼에 "로그인 중..." 표시 및 로딩 애니메이션 추가
        loginButton.disabled = true;
        loginButton.textContent = "로그인 중...";
        const spinner = document.createElement('div');
        spinner.classList.add('spinner'); // CSS로 정의된 로딩 스피너 클래스
        loginButton.appendChild(spinner);

        // AJAX 요청을 통해 사용자 정보 가져오기
        fetch(GET_USER_INFO, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"), // CSRF 토큰
            },
            body: JSON.stringify({
                sToken: sToken,
                sIdno: sIdno,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                setTimeout(() => {
                    if (data.success) {
                        const userInfo = data.user_info;
                        const isAIX = userInfo.department === "AI융합학부";
                        const isEnrolled = userInfo.is_enrolled === "학사과정 재학";

                        if (!isAIX) {
                            // 학부가 다른 경우
                            loginButton.textContent = "로그인 실패";
                            displayErrorMessage(
                                "AI융합학부 학생만 이용 가능합니다."
                            );
                        } else if (!isEnrolled) {
                            // 재학 여부가 아닌 경우
                            loginButton.textContent = "로그인 실패";
                            displayErrorMessage(
                                "재학생만 이용 가능합니다."
                            );
                        } else {
                            // 모든 조건을 만족할 경우 예약 페이지로 리디렉션
                            loginButton.textContent = "로그인 성공";
                            displayErrorMessage(
                                "잠시 후 예약 페이지로 이동합니다.",
                                "text-blue-500"
                            );
                            setTimeout(() => {
                                window.location.href = RESERVATION;
                            }, 1500);
                        }
                    } else {
                        // 전체 오류 메시지 표시
                        displayErrorMessage("로그인 실패. 다시 시도해주세요.");
                    }
                }, 2000); // 2초 대기 후 결과 표시
            })
            .catch((error) => {
                console.error("Error:", error);
                setTimeout(() => {
                    displayErrorMessage(
                        "로그인 과정에서 오류가 발생했습니다. 다시 시도해주세요."
                    );
                }, 2000); // 2초 대기 후 오류 표시
            })
            .finally(() => {
                // 모든 경우에 로그인 데이터를 삭제
                clearLoginData();
            });
    }
};

// 로그인 실패 또는 기타 메시지 출력 함수
function displayErrorMessage(message, color = "text-red-500") {
    const errorMessage = document.getElementById("error-message");

    // 기존의 색상 클래스 제거
    errorMessage.className = "error-message font-semibold mt-4";

    // 동적으로 색상 클래스 추가
    errorMessage.classList.add(color);

    // 에러 메시지 업데이트
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden"); // 숨김 해제

    // 1초 후 버튼 복원
    setTimeout(() => {
        const loginButton = document.getElementById("login-button");
        loginButton.disabled = false; // 버튼 활성화
        loginButton.innerHTML = `
            <span id="login-text">통합 로그인</span>
            <img id="login-icon" src="${AIX_LOGO}" alt="로그인 아이콘" class="login-icon">
        `;
    }, 2000);
}



// 로그인 데이터 삭제 함수
function clearLoginData() {
    // 쿠키 삭제
    document.cookie =
        "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

// CSRF 토큰 가져오기 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
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

document.addEventListener('DOMContentLoaded', () => {
    const infoButton = document.getElementById('info-button');
    const developerInfo = document.getElementById('developer-info');
    const toggleIcon = document.getElementById('toggle-icon');

    infoButton.addEventListener('click', () => {
        developerInfo.classList.toggle('hidden');
        toggleIcon.classList.toggle('rotate-180'); // 아이콘 회전
    });
});


// 오늘 날짜를 설정하는 함수
function setCurrentDate() {
    const currentDateElement = document.getElementById("current-date");
    const today = new Date();

    // 날짜를 'MM/DD' 형식으로 변환
    const formattedDate = `${String(today.getMonth() + 1).padStart(2, '0')}/${String(today.getDate()).padStart(2, '0')}`;

    // HTML에 날짜 설정
    currentDateElement.textContent = formattedDate;
}

// 페이지 로드 시 오늘 날짜 설정
document.addEventListener("DOMContentLoaded", setCurrentDate);