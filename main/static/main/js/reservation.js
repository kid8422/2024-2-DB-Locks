document.addEventListener("DOMContentLoaded", async () => {
    const locker_data = LOAD_4F;
    await select_floor("4F", locker_data);
    await loadReservationDetails();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function reserveLocker(lockerNum) {
    const studentId = STUDENT_ID; // Django Template에서 전달된 사용자 ID
    const studentName = STUDENT_NAME;
    const studnetDepartment = STUDENT_DEPARTMENT;
    const requestData = {
        locker_num: lockerNum,
        student_id: studentId,
        student_name: studentName,
        student_department: studnetDepartment
    };

    try {
        const response = await fetch(RESERVE_LOCKER, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(requestData),
        });

        const result = await response.json();

        if (result.success) {
            showSuccessModal(lockerNum, result.message);
        } else {
            showFailModal(lockerNum, result.message);
        }
    } catch (error) {
        console.error("예약 중 오류 발생:", error);
    }
}

async function select_floor(activeFloor, locker_data) {
    const btn4F = document.getElementById("btn-4F");
    const btnB1 = document.getElementById("btn-B1");
    const map = document.getElementById("map-image");
    try {
        const response = await fetch(locker_data);
        if (!response.ok) {
            throw new Error('네트워크 응답이 올바르지 않습니다.');
        }
        const data = await response.json();

        const lockerGrid = document.getElementById("locker-grid");
        lockerGrid.innerHTML = ""; // 기존 사물함 지우기

        // 사물함 데이터 처리
        data.rows.forEach(locker => {
            const button = document.createElement("button");
            button.className = "locker-item";
            button.disabled = locker["대여 구분"] !== "available"; // "available"이 아니면 버튼 비활성화

            // 버튼 내용 설정
            button.innerHTML = `
                <div class="locker-label">
                    ${locker["대여 구분"] === "available" ? "예약 가능" : "대여 중"}
                </div>
                <hr class="my-1 w-8 border-gray-300">
                <div class="locker-number">${locker["사물함 번호"]}</div>
            `;

            // 예약 가능 상태인 경우 클릭 이벤트 추가
            if (locker["대여 구분"] === "available") {
                button.addEventListener("click", () => {
                    highlightSelectedLocker(button);
                    showSelectedLocker(activeFloor, locker["사물함 번호"]); // 선택한 사물함 표시
                });
            }

            // 버튼을 그리드에 추가
            lockerGrid.appendChild(button);
        });




    } catch (error) {
        console.error("Error loading data:", error);
        throw error; // 에러를 상위로 전달
    }
    if (activeFloor === "4F") {
        btn4F.classList.remove("bg-gray-200", "text-black");
        btn4F.classList.add("bg-blue-500", "text-white");
        btnB1.classList.remove("bg-blue-500", "text-white");
        btnB1.classList.add("bg-gray-200", "text-black");
        map.src = MAP_4F;
    } else if (activeFloor === "B1") {
        btn4F.classList.remove("bg-blue-500", "text-white");
        btn4F.classList.add("bg-gray-200", "text-black");
        btnB1.classList.remove("bg-gray-200", "text-black");
        btnB1.classList.add("bg-blue-500", "text-white");
        map.src = MAP_B1;
    }

};


function highlightSelectedLocker(selectedElement) {
    const allLockers = document.querySelectorAll(".locker-item");

    // 모든 사물함의 선택 상태 초기화
    allLockers.forEach(locker => locker.classList.remove("selected"));

    // 선택된 사물함에만 선택 클래스 추가
    selectedElement.classList.add("selected");
}

// 선택한 사물함 번호를 표시하는 함수
function showSelectedLocker(activeFloor, lockerNumber) {
    const reservationInfoContainer = document.querySelector(".reservation-status");
    reservationInfoContainer.innerHTML = `
        <div class="selected-locker-info">
            <p class="selected-locker-title">선택된 사물함</p>
            <p id="selected-floor" class="selected-floor">${activeFloor}</p>
            <p id="selected-locker-number" class="selected-locker-number">${lockerNumber}</p>
            <button class="reserve-button" onclick="showReservationModal(${lockerNumber})">예약하기</button>
        </div>
    `;
}



// Modal 열기 및 닫기 함수
function showReservationModal(lockerNumber) {
    const modal = document.getElementById("reservation-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalMessage = document.getElementById("modal-message");
    const confirmButton = document.getElementById("modal-confirm");
    const cancelButton = document.getElementById("modal-cancel");

    // Modal 메시지 설정
    modalTitle.textContent = "예약 확인";
    modalMessage.textContent = `${lockerNumber}번 사물함을 예약하시겠습니까?`;

    // Modal 표시
    modal.classList.remove("hidden");

    // 확인 버튼 클릭 이벤트
    confirmButton.onclick = () => {
        modal.classList.add("hidden");
        reserveLocker(lockerNumber);
    };

    // 취소 버튼 클릭 이벤트
    cancelButton.onclick = () => {
        modal.classList.add("hidden");
    };
}


// 예약 현황 창 업데이트 함수
function updateReservationPanel(floor, lockerNumber, startDate, endDate) {
    const reservationDetails = document.getElementById("reservation-details");

    const [startDateOnly, startTime] = startDate.split(" "); // 날짜와 시간 분리
    const [endDateOnly, endTime] = endDate.split(" "); // 날짜와 시간 분리

    reservationDetails.innerHTML = `
        <div class="reservation-info">
            <div class="locker-details">
                <p class="selected-floor">${floor}</p> <!-- 층 정보 -->
                <p class="selected-locker-number">${lockerNumber}</p> <!-- 사물함 번호 -->
                <button class="return-button" onclick="returnLocker(${lockerNumber})">반납하기</button> <!-- 반납 버튼 -->
            </div>
            <div class="rental-period">
                <p class="value">
                    <span class="date">${startDateOnly}</span> 
                    <span class="time">${startTime}</span> ~ 
                    <span class="date">${endDateOnly}</span> 
                    <span class="time">${endTime}</span>
                </p>
            </div>
        </div>
    `;
    
}

// 예약 완료 후 호출
function showSuccessModal(lockerNumber, message) {
    const successModal = document.getElementById("reservation-success-modal");
    const successMessage = document.getElementById("success-message");
    const closeButton = document.getElementById("success-close");

    successMessage.textContent = `${lockerNumber}번 사물함이 성공적으로 예약되었습니다.`;

    // 모달 표시
    successModal.classList.remove("hidden");

    // 닫기 버튼 클릭 이벤트
    closeButton.onclick = () => {
        successModal.classList.add("hidden");
        location.reload(); // 예약 후 페이지 새로고침
    };
}

// 예약 완료 후 호출
function showFailModal(lockerNumber, message) {
    const successModal = document.getElementById("reservation-success-modal");
    const successMessage = document.getElementById("success-message");
    const closeButton = document.getElementById("success-close");

    successMessage.textContent = `${message}`;

    // 모달 표시
    successModal.classList.remove("hidden");

    // 닫기 버튼 클릭 이벤트
    closeButton.onclick = () => {
        successModal.classList.add("hidden");
        location.reload(); // 예약 후 페이지 새로고침
    };
}

function showMessage(message) {
    const successModal = document.getElementById("reservation-success-modal");
    const successMessage = document.getElementById("success-message");
    const closeButton = document.getElementById("success-close");

    successMessage.textContent = `${message}`;

    // 모달 표시
    successModal.classList.remove("hidden");

    // 닫기 버튼 클릭 이벤트
    closeButton.onclick = () => {
        successModal.classList.add("hidden");
        location.reload(); // 예약 후 페이지 새로고침
    };
}

function confirmReservation() {
    const selectedFloor = document.getElementById("selected-floor").textContent; // 선택된 층
    const selectedLockerNumber = document.getElementById("selected-locker-number").textContent; // 선택된 사물함 번호

    if (!selectedLockerNumber || !selectedFloor) {
        alert("예약할 사물함을 먼저 선택해주세요!");
        return;
    }

    showReservationModal(selectedLockerNumber); // 예약 확인 모달 표시
}

async function loadReservationDetails() {
    const reservationDetailsContainer = document.getElementById("reservation-details");

    try {
        const requestData = {
            student_id: STUDENT_ID
        }
        const response = await fetch(MYRESERVATIONINFO, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();

        if (result.success && result.data) {
            const { floor, locker_num, start_date, end_date } = result.data;
            updateReservationPanel(floor, locker_num, start_date, end_date); // 실제 층 정보는 필요시 DB에서 추가
        } else {
            reservationDetailsContainer.innerHTML = `
                <p class="no-reservation">예약한 사물함 정보가 없습니다.</p>
            `;
        }
    } catch (error) {
        console.error("Error loading reservation details:", error);
        reservationDetailsContainer.innerHTML = `
            <p class="no-reservation">예약 정보를 가져오는 중 오류가 발생했습니다.</p>
        `;
    }
}

async function returnLocker(lockerNum) {
    try {
        const requestData = {
            student_id: STUDENT_ID,
            locker_num: lockerNum,
        }
        const response = await fetch(RETURN_LOCKER, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (result.success) {
            showMessage(`${lockerNum}번 사물함이 성공적으로 반납되었습니다.`);
        } else {
            showMessage(`사물함 반납에 실패하였습니다. 다시 시도해 주세요.`);
        }
    } catch (error) {
        console.error("Error returning locker:", error);
        alert("반납 중 오류가 발생했습니다.");
    }
}