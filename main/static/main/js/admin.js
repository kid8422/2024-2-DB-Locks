async function loadData(DBname) {
    try {
        const response = await fetch(DBname);
        if (!response.ok) {
            throw new Error('네트워크 응답이 올바르지 않습니다.');
        }
        const data = await response.json();

        const dataHead = document.getElementById('data-head');
        dataHead.innerHTML = ""; // 기존 내용 초기화

        const dataBody = document.getElementById('data-body');
        dataBody.innerHTML = ""; // 기존 내용 초기화

        const head = data.head;
        const rows = data.rows;

        // 헤더 생성
        const trHead = document.createElement('tr'); // 헤더 행 생성
        head.forEach(col => {
            const th = document.createElement('th'); // 헤더 셀 생성
            th.textContent = col; // 헤더 텍스트 설정
            trHead.appendChild(th); // 헤더 행에 추가
        });
        dataHead.appendChild(trHead); // 테이블 헤더 추가

         // 데이터가 없는 경우 처리
         if (rows.length === 0) {
            const trEmpty = document.createElement('tr');
            const tdEmpty = document.createElement('td');
            tdEmpty.textContent = "데이터가 존재하지 않습니다.";
            tdEmpty.colSpan = head.length; // 전체 열 병합
            tdEmpty.style.textAlign = "center"; // 가운데 정렬
            tdEmpty.style.padding = "10px"; // 간격 조정
            trEmpty.appendChild(tdEmpty);
            dataBody.appendChild(trEmpty);
            return; // 더 이상 데이터 처리 없음
        }

        // 데이터 행 생성
        rows.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.style.backgroundColor = index % 2 === 0 ? "#ffffff" : "#f0f0f0"; // 홀수/짝수 색 구분

            head.forEach(col => {
                const td = document.createElement('td');
                td.textContent = row[col];
                td.style.padding = "10px"; // 간격 조정
                tr.appendChild(td);
            });
            dataBody.appendChild(tr);
        });
    } catch (error) {
        console.error("Error loading data:", error);
        throw error; // 에러를 상위로 전달
    }
}