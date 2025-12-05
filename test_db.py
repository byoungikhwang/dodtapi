# # ... (위의 연결 코드 생략) ...

# cur.execute("SELECT * FROM users")
# rows = cur.fetchall() # 모든 데이터를 가져옴

# print("=== 회원 목록 ===")
# for row in rows:
#     print(row) 

# # ... (종료 코드) ...

# # ... DB 연결 코드 생략  자료 추가...
# sql = "INSERT INTO users (user_id, password) VALUES (%s, %s)"
# data = ("saintjin9", "sj112233@")

# cur.execute(sql, data)
# conn.commit()  # <--- 중요! 이걸 해야 실제로 저장이 완료됩니다.

# # sql db 생성
# CREATE TABLE users (
#     id SERIAL PRIMARY KEY,
#     user_id VARCHAR(50) NOT NULL,
#     password VARCHAR(100) NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# # 자료 추가
# INSERT INTO users (user_id, password) 
# VALUES ('saintjin9', 'sj112233@');

# # 자료 확인
# SELECT * FROM users;
# # 글 로그인 사용자는 비밀번호가 없으므로, 비밀번호 칸을 비워둬도 되도록(NULL 허용)
# ALTER TABLE users ALTER COLUMN password DROP NOT NULL;

# # 자료 추가
# UPDATE users
# SET password = 'new_password_1234'
# WHERE user_id = 'saintjin9@gmail.com';

# # 자료 삭제
# DELETE FROM users
# WHERE user_id = 'saintjin9@gmail.com';