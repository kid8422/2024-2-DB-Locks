import pymysql
from datetime import datetime, timedelta

# 데이터베이스 연결 정보
host = '127.0.0.1'
# host = '10.27.18.99'
port = 3306
user = 'root'  # MySQL 사용자명
# user = 'Locks'
password = 'password'  # MySQL 비밀번호
database = 'db_locks'  # 사용할 데이터베이스

# 데이터베이스 연결
conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    passwd=password,
    db=database
)

cursor = conn.cursor()

# lockers 테이블에 있는 모든 값 출력
def find_all_lockers():
    sql_query = "select * from lockers"
    cursor.execute(sql_query)

    result = cursor.fetchall()
    # for row in result:
    #     print(row)

    return result


# rent 테이블에 있는 모든 값 출력
def find_all_rent():
    sql_query = "select * from rent"
    cursor.execute(sql_query)

    result = cursor.fetchall()
    # for row in result:
    #     print(row)

    return result


# student 테이블에 있는 모든 값 출력
def find_all_student():
    sql_query = "select * from student"
    cursor.execute(sql_query)

    result = cursor.fetchall()
    # for row in result:
    #     print(row)

    return result

# log 테이블에 있는 모든 값 출력
def find_all_log():
    sql_query = "select * from log"
    cursor.execute(sql_query)

    result = cursor.fetchall()
    # for row in result:
    #     print(row)

    return result

# show tables;
def show_tables():
    sql_query = "show tables"
    cursor.execute(sql_query)

    result = cursor.fetchall()

    for row in result:
        print(row)

# student 테이블에 값 삽입하는 함수
def insert_into_student(student_id:int, name, department):  # 반납되어도 학적 정보 저장해둠
    # INSERT INTO SQL 쿼리
    insert_query = """
    INSERT INTO student (student_id, name, department)
    VALUES (%s, %s, %s)
    """

    # 쿼리 실행
    cursor.execute(insert_query, (student_id, name, department))

    # 변경 사항 커밋
    conn.commit()

    find_all_student()

# rent 테이블에 값 삽입하는 함수
def insert_into_rent(locker_num:int, student_id:int, rent_type, start_date, end_date):    # 반납이 되면 지워지도록 해야함
    insert_query = """
    INSERT INTO rent (locker_num, student_id, rent_type, start_date, end_date)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, (locker_num, student_id, rent_type, start_date, end_date))

    conn.commit()

    find_all_rent()

# lockers 테이블을 업데이트하는 함수
def insert_into_lockers(locker_num:int, rental_state):  # 사물함 빌림 함수
    update_query = """
    UPDATE lockers
    SET rental_state = %s
    WHERE locker_num = %s
    """

    cursor.execute(update_query, (locker_num, rental_state))    # rental_state는 long 또는 short 또는 available
    conn.commit()

    find_all_lockers()

# log 테이블을 삽입하거나 업데이트하는 함수
def insert_into_log(student_id:int, start_date, end_date):
    insert_query = """
    INSERT INTO log (student_id, start_date, end_date)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (student_id, start_date, end_date))
    conn.commit()
    
    find_all_log()

# log 테이블에 학번을 넘겨주어서 column을 반환 (2차원 튜플로 생성됨)
def find_from_log(student_id:int):
    find_query = """
    SELECT * FROM log
    WHERE student_id = %s
    """

    cursor.execute(find_query, (student_id))
    result_find = cursor.fetchall()
    print(result_find)
    return result_find

# student 테이블에 학번을 넘겨주어서 column을 반환 (2차원 튜플로 생성됨)
def find_from_student(student_id:int):
    find_query = """
    SELECT * FROM student
    WHERE student_id = %s
    """

    cursor.execute(find_query, (student_id))
    result_find = cursor.fetchall()
    print(result_find)
    return result_find

# lockers 테이블에 사물함 번호를 넘겨주어서 column을 반환 (2차원 튜플로 생성됨)
def find_from_lockers(locker_num:int):
    find_query = """
    SELECT * FROM lockers
    WHERE locker_num = %s
    """
    cursor.execute(find_query, (locker_num))
    result_find = cursor.fetchall()
    print(result_find)
    return result_find

# rent 테이블에 학번을 넘겨주어서 rent와 student의 natural join column을 반환 ((student_id, locker_num, rent_type, start_date, end_date, name, department),)
def find_from_rent(student_id:int):
    find_query = """
    select * from rent
    natural join student
    where rent.student_id = %s;
    """
    cursor.execute(find_query, (student_id))
    result_find = cursor.fetchall()
    # print(result_find)
    return result_find

# student 테이블에서 학번으로 검색해 해당 column 삭제
def delete_from_student(student_id:int):
    delete_query = """
    DELETE FROM student
    WHERE student_id = %s
    """
    cursor.execute(delete_query, (student_id))
    conn.commit()
    find_all_student()

# rent 테이블에서 사물함 번호로 검색해 해당 column 삭제
def delete_from_rent(locker_num:int):
    delete_query = """
    DELETE FROM rent
    WHERE locker_num = %s
    """
    cursor.execute(delete_query, (locker_num))
    conn.commit()
    find_all_rent()

# lockers 테이블에서 사물함 번호로 검색해 해당 사용 상태를 available로 변환
def delete_from_lockers(locker_num:int):    # 사물함 반납 함수
    update_query = """
    UPDATE lockers
    SET rental_state = %s
    WHERE locker_num = %s
    """

    cursor.execute(update_query, (locker_num, 'available'))
    conn.commit()
    find_all_lockers()

# log 내용 전부 비움
def clear_log():
    delete_query = """
    TRUNCATE TABLE log
    """
    cursor.execute(delete_query)
    conn.commit()
    find_all_log()

    ##################################################################################################################################


## 예약 프로세스

def reservation_process(locker_num:int, student_id:int, name, department, rent_type):
    if (find_from_lockers(locker_num)[0][2] != 'available'):    # 예약하려는 사물함 번호가 이미 예약된 경우 예약 불가
        print("대여 불가능")
        
    elif (len(find_from_rent(student_id)) != 0):    # 해당 학번으로 이미 빌린 사물함이 존재하는 경우 예약 불가
        print(f"{student_id} 학번으로 빌린 사물함이 이미 존재합니다.")
        
    else:
        now = datetime.now()
        insert_into_student(student_id, name, department)
        insert_into_lockers(locker_num, rent_type)

        if (rent_type == 'long'):
            end = now + timedelta(days=120)     # 한 학기를 120일로 지정
            start_date = now.strftime("%Y-%m-%d %H:%M:%S")
            end_date = end.strftime("%Y-%m-%d %H:%M:%S")
            insert_into_rent(locker_num, student_id, rent_type, start_date, end_date)
        
        if (rent_type == 'short'):
            end = now + timedelta(days=3)     # 단기 대여는 3일로 지정
            start_date = now.strftime("%Y-%m-%d %H:%M:%S")
            end_date = end.strftime("%Y-%m-%d %H:%M:%S")
            insert_into_rent(locker_num, student_id, rent_type, start_date, end_date)
        
        #### log는 반납이 완료되면 rent에서 학번으로 검색해서 불러오는 방식으로 구현



# 두 날짜를 비교하여 첫 번째 날짜가 두 번째 날짜보다 앞선다면 True를 반환
def is_first_date_earlier(date1, date2):
    """
    :param date1: 첫 번째 날짜 (형식: YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS)
    :param date2: 두 번째 날짜 (형식: YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS)
    :return: 첫 번째 날짜가 앞서면 True, 그렇지 않으면 False
    """
    # 날짜 형식을 파싱
    format_str = "%Y-%m-%d %H:%M:%S"
    dt1 = datetime.strptime(date1, format_str)
    dt2 = datetime.strptime(date2, format_str)

    # 날짜 비교
    return dt1 < dt2


## 반납 프로세스

def return_process(locker_num:int, student_id:int):     # 기간이 지나기 전에 알아서 반납
    now = datetime.now()
    start_date = find_from_rent(student_id)[0][3]
    end_date = find_from_rent(student_id)[0][4]

    if (is_first_date_earlier(now, end_date)):
        delete_from_rent(locker_num)
        delete_from_student(student_id)
        delete_from_lockers(locker_num)
        insert_into_log(student_id, start_date, now)

def out_process():      # rent 테이블 전체를 검사해서 기간이 지나면 자동으로 반납
    now = datetime.now()
    result_find = find_all_rent()

    for i in range(len(result_find)):
        locker_num, student_id, _, start_date, end_date = result_find[i]
        if (not is_first_date_earlier(now, end_date)):
            delete_from_rent(locker_num)
            delete_from_student(student_id)
            delete_from_lockers(locker_num)
            insert_into_log(student_id, start_date, end_date)


## 나의 예약 현황에 보이는 대여 기간 표시 함수

def check_my_info(student_id:int):
    start_date = find_from_rent(student_id)[0][3]
    end_date = find_from_rent(student_id)[0][4]

    string = f"{start_date.strftime('%Y-%m-%d %H:%M')} ~ {end_date.strftime('%Y-%m-%d %H:%M')}"
    return string

cursor.close()
conn.close()