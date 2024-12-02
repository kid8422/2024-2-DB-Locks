// admin.js

let currentTableURL = null; // 현재 선택된 테이블 URL
let currentHead = []; // 현재 테이블 헤더
let currentTable = ''; // 현재 선택된 테이블 이름

// Display Name to DB Field Name Mapping
const fieldMapping = {
    '사물함 번호': 'locker_num',
    'TAG': 'TAG',
    '대여 여부': 'rental_state',
    '이름': 'name',
    '학번': 'student_id',
    '학과(부)': 'department',
    '대여 구분': 'rent_type',
    '대여 시작 날짜': 'start_date',
    '대여 종료 날짜': 'end_date'
};

// Mapping from URL to table name
const urlToTableName = {
    [LOCKERS]: 'lockers',
    [RENT]: 'rent',
    [LOG]: 'log',
    [STUDENT]: 'student'
};

// 데이터 로드 함수
async function loadData(DBname) {
    try {
        currentTableURL = DBname; // 현재 URL 저장
        localStorage.setItem('currentTableURL', currentTableURL); // 로컬스토리지에 저장
        console.log(`Loading data from: ${DBname}`);

        // Set currentTable based on DBname
        currentTable = urlToTableName[DBname];
        console.log(`Current Table: ${currentTable}`);

        const response = await fetch(DBname);
        if (!response.ok) {
            throw new Error('네트워크 응답이 올바르지 않습니다.');
        }
        const data = await response.json();
        console.log('Data fetched:', data);

        const dataHead = document.getElementById('data-head');
        dataHead.innerHTML = ""; // 기존 헤더 초기화

        const dataBody = document.getElementById('data-body');
        dataBody.innerHTML = ""; // 기존 바디 초기화

        const head = data.head;
        currentHead = head; // 글로벌 변수에 헤더 저장
        const rows = data.rows;

        console.log('Table Head:', head);
        console.log('Table Rows:', rows);

        // 헤더에 'Actions' 열 추가
        const trHead = document.createElement('tr');
        head.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            th.classList.add('px-4', 'py-2'); // 패딩 추가
            trHead.appendChild(th);
        });
        const actionsTh = document.createElement('th');
        actionsTh.textContent = ""; // 'Actions' 열 제목 비워둠
        actionsTh.classList.add('w-24', 'text-center', 'px-4', 'py-2'); // 너비 및 정렬 클래스 추가
        trHead.appendChild(actionsTh);
        dataHead.appendChild(trHead);
        console.log('Actions column added to header.');

        // 데이터가 없는 경우 처리
        if (rows.length === 0) {
            const trEmpty = document.createElement('tr');
            const tdEmpty = document.createElement('td');
            tdEmpty.textContent = "데이터가 존재하지 않습니다.";
            tdEmpty.colSpan = head.length + 1; // Actions 열 포함
            tdEmpty.classList.add('text-center', 'p-4');
            trEmpty.appendChild(tdEmpty);
            dataBody.appendChild(trEmpty);
            console.log('No data available.');
            return;
        }

        // 데이터 행 생성
        rows.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.classList.add(index % 2 === 0 ? 'bg-white' : 'bg-gray-100');

            head.forEach(col => {
                const td = document.createElement('td');
                td.textContent = row[col] !== null ? row[col] : '';
                td.classList.add('px-4', 'py-2'); // 패딩 추가
                tr.appendChild(td);
            });

            // '수정하기' 버튼 추가
            const editTd = document.createElement('td');
            editTd.classList.add('w-24', 'text-center', 'px-4', 'py-2'); // 너비 및 정렬 클래스 추가
            const editButton = document.createElement('button');
            editButton.textContent = "수정하기";
            editButton.classList.add('px-1', 'py-1', 'bg-yellow-500', 'text-white', 'rounded', 'shadow', 'hover:bg-yellow-600');
            editButton.onclick = () => openEditModal(row);
            editTd.appendChild(editButton);
            tr.appendChild(editTd);
            console.log(`Edit button added for row: ${JSON.stringify(row)}`);

            dataBody.appendChild(tr);
        });
    } catch (error) {
        console.error("Error loading data:", error);
        alert("데이터 로드 중 오류가 발생했습니다.");
    }
}

// 수정 모달 열기 함수
function openEditModal(row) {
    console.log('Opening edit modal for row:', row);
    const modal = document.getElementById('edit-modal');
    const formFields = document.getElementById('form-fields');
    formFields.innerHTML = ''; // 기존 필드 초기화

    // 동적으로 폼 필드 생성
    currentHead.forEach(col => {
        const fieldDiv = document.createElement('div');
        fieldDiv.classList.add('form-field', 'mb-4');

        const label = document.createElement('label');
        label.textContent = col;
        label.setAttribute('for', `field-${col}`);
        label.classList.add('block', 'text-sm', 'font-medium', 'text-gray-700');
        fieldDiv.appendChild(label);

        let input;
        if (col === '대여 여부') { // "대여 여부" 필드인 경우 select 요소 생성
            input = document.createElement('select');
            input.id = `field-${col}`;
            input.name = col;
            input.setAttribute('aria-label', '대여 여부'); // 접근성 향상을 위한 aria-label 추가
            input.classList.add('mt-1', 'block', 'w-full', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm', 'focus:ring-blue-500', 'focus:border-blue-500');

            const options = ["이용 가능", "장기 대여", "단기 대여", "사용 불가"];
            options.forEach(optionText => {
                const option = document.createElement('option');
                option.value = optionText;
                option.textContent = optionText;
                if (row[col] === optionText) {
                    option.selected = true;
                }
                input.appendChild(option);
            });
        } else {
            // 다른 필드는 기존과 동일하게 input 요소 생성
            input = document.createElement('input');
            input.type = 'text';
            input.id = `field-${col}`;
            input.name = col;
            input.value = row[col] !== null ? row[col] : '';
            input.classList.add('mt-1', 'block', 'w-full', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm', 'focus:ring-blue-500', 'focus:border-blue-500');

            // 특정 테이블에서 특정 필드 수정 불가능하게 설정
            if ((currentTable === 'lockers') && ((col === '사물함 번호') || (col === '위치'))) {
                input.disabled = true; // 수정 불가능하게 설정
                input.classList.add('disabled-input'); // CSS 클래스 추가
            }
            if ((currentTable === 'rent') && ((col === '사물함 번호') || (col === '이름') || (col === '학과(부)'))) {
                input.disabled = true; // 수정 불가능하게 설정
                input.classList.add('disabled-input'); // CSS 클래스 추가
            }
            if ((currentTable === 'log') && ((col === '이름') || (col === '학번') || (col === '학과(부)'))) {
                input.disabled = true; // 수정 불가능하게 설정
                input.classList.add('disabled-input'); // CSS 클래스 추가
            }
            if ((currentTable === 'student') && (col === '학번')) {
                input.disabled = true; // 수정 불가능하게 설정
                input.classList.add('disabled-input'); // CSS 클래스 추가
            }
        }

        fieldDiv.appendChild(input);
        formFields.appendChild(fieldDiv);
    });

    // 폼에 기본 키 저장 (가정: 첫 번째 열이 기본 키)
    const pkField = currentHead[0];
    formFields.dataset.pk = row[pkField];
    console.log(`Primary key (${pkField}):`, row[pkField]);

    document.body.classList.add('modal-open');
    modal.classList.remove('hidden');
}

// 수정 모달 닫기 함수
function closeEditModal() {
    const modal = document.getElementById('edit-modal');
    modal.classList.add('hidden');
    document.body.classList.remove('modal-open');
    console.log('Edit modal closed.');
}

// CSRF 토큰 가져오기 함수
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

// 폼 제출 이벤트 처리
async function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formFields = document.getElementById('form-fields');
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    // 기본 키 가져오기
    const pk = formFields.dataset.pk;
    data['pk'] = pk;
    console.log('Form data submitted:', data);

    // '대여 여부' 값을 코드로 변환
    if (data['대여 여부']) {
        const rentalStateMapping = {
            "이용 가능": "available",
            "장기 대여": "long",
            "단기 대여": "short",
            "사용 불가": "unavailable"
        };
        data['rental_state'] = rentalStateMapping[data['대여 여부']] || data['rental_state'];
        delete data['대여 여부']; // 불필요한 필드 제거
    }

    console.log('Request Data:', data);

    // 테이블 이름 추가
    data['table_name'] = currentTable;

    // 업데이트 요청 전송
    try {
        const response = await fetch(UPDATE, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error('업데이트 요청 실패');
        }
        const result = await response.json();
        console.log('Update response:', result);
        if (result.success) {
            closeEditModal();
            loadData(currentTableURL); // 데이터 새로고침
        } else {
            alert('업데이트 중 오류가 발생했습니다: ' + result.error);
        }
    } catch (error) {
        console.error('Error updating data:', error);
        alert('업데이트 중 오류가 발생했습니다.');
    }
}

// DOMContentLoaded 이벤트 핸들러
document.addEventListener('DOMContentLoaded', () => {
    // 이전에 선택된 테이블 불러오기
    const savedTableURL = localStorage.getItem('currentTableURL');
    if (savedTableURL) {
        loadData(savedTableURL);
    }

    // 'close-modal'과 'cancel-edit' 버튼 이벤트 리스너 추가
    const closeModalButton = document.getElementById('close-modal');
    const cancelEditButton = document.getElementById('cancel-edit');

    if (closeModalButton) {
        closeModalButton.addEventListener('click', closeEditModal);
    } else {
        console.error("'close-modal' 버튼을 찾을 수 없습니다.");
    }

    if (cancelEditButton) {
        cancelEditButton.addEventListener('click', closeEditModal);
    } else {
        console.error("'cancel-edit' 버튼을 찾을 수 없습니다.");
    }

    // 폼 제출 이벤트 리스너 추가
    const editForm = document.getElementById('edit-form');
    if (editForm) {
        editForm.addEventListener('submit', handleFormSubmit);
    } else {
        console.error("'edit-form' 폼을 찾을 수 없습니다.");
    }
});
