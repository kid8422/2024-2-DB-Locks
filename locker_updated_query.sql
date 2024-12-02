show databases;
use db_locks;
show tables;

-- INSERT INTO lockers (locker_num, TAG)
-- VALUES 
--     (1, 'B1'), (2, 'B1'), (3, 'B1'), (4, 'B1'), (5, 'B1'),
--     (6, 'B1'), (7, 'B1'), (8, 'B1'), (9, 'B1'), (10, 'B1'),
--     (11, 'B1'), (12, 'B1'), (13, 'B1'), (14, 'B1'), (15, 'B1'),
--     (16, 'B1'), (17, 'B1'), (18, 'B1'), (19, 'B1'), (20, 'B1');

-- -- 21부터 90까지 TAG = '4F'
-- INSERT INTO lockers (locker_num, TAG)
-- VALUES 
--     (21, '4F'), (22, '4F'), (23, '4F'), (24, '4F'), (25, '4F'),
--     (26, '4F'), (27, '4F'), (28, '4F'), (29, '4F'), (30, '4F'),
--     (31, '4F'), (32, '4F'), (33, '4F'), (34, '4F'), (35, '4F'),
--     (36, '4F'), (37, '4F'), (38, '4F'), (39, '4F'), (40, '4F'),
--     (41, '4F'), (42, '4F'), (43, '4F'), (44, '4F'), (45, '4F'),
--     (46, '4F'), (47, '4F'), (48, '4F'), (49, '4F'), (50, '4F'),
--     (51, '4F'), (52, '4F'), (53, '4F'), (54, '4F'), (55, '4F'),
--     (56, '4F'), (57, '4F'), (58, '4F'), (59, '4F'), (60, '4F'),
--     (61, '4F'), (62, '4F'), (63, '4F'), (64, '4F'), (65, '4F'),
--     (66, '4F'), (67, '4F'), (68, '4F'), (69, '4F'), (70, '4F'),
--     (71, '4F'), (72, '4F'), (73, '4F'), (74, '4F'), (75, '4F'),
--     (76, '4F'), (77, '4F'), (78, '4F'), (79, '4F'), (80, '4F'),
--     (81, '4F'), (82, '4F'), (83, '4F'), (84, '4F'), (85, '4F'),
--     (86, '4F'), (87, '4F'), (88, '4F'), (89, '4F'), (90, '4F');

select * from lockers;

insert into student (student_id, name, department)
value
(20233109, "장재혁", "AI융합학부");
select * from student;

insert into rent (locker_num, student_id, rent_type, start_date, end_date)
value
(3, 20233109, 'long', '2024-11-30 11:30:00', '2024-12-04 11:30:00');
select * from rent;

update lockers
set rental_state = 'long'
where locker_num = 3;
select * from lockers where rental_state = 'long';

select * from log;

insert into log (student_id, start_date, end_date)
value (20233109, '2024-11-30 11:30:00', '2024-12-04 11:30:00');
select * from log;

select * from rent;

