document.addEventListener("DOMContentLoaded", async () => {
    const locker_data = LOAD_4F;
    await select_floor("4F", locker_data);
});

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
                    alert(`${locker["사물함 번호"]}번 사물함을 예약했습니다.`);
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


// 예약 정보 (가정: DB에서 불러오는 변수)
const reservationData = {
    lockerNumber: 28,
    startDate: "2024-11-28",
    rentalPeriod: "30일",
};


// 나의 예약 현황 확인
myReservationBtn.addEventListener("click", () => {
    reservationInfo.innerHTML = `
        <div class="status-card">
            <p class="status-item font-bold text-lg text-blue-600">예약한 사물함 정보</p>
            <p class="status-item">사물함 번호: <span class="font-bold">${reservationData.lockerNumber}</span></p>
            <p class="status-item">대여 날짜: <span class="font-bold">${reservationData.startDate}</span></p>
            <p class="status-item">대여 기간: <span class="font-bold">${reservationData.rentalPeriod}</span></p>
        </div>
    `;
});

