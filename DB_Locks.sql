-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema locker
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema locker
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `DB_Locks`;
CREATE SCHEMA IF NOT EXISTS `DB_Locks` DEFAULT CHARACTER SET utf8 ;
SHOW WARNINGS;
USE `DB_Locks` ;

-- -----------------------------------------------------
-- Table `locker`.`lockers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `DB_Locks`.`lockers`;
CREATE TABLE IF NOT EXISTS `DB_Locks`.`lockers` (
  `locker_num` INT UNSIGNED NOT NULL,
  `TAG` VARCHAR(5) NOT NULL,
  `rental_state` ENUM('available', 'long', 'short') NOT NULL DEFAULT 'available',
  PRIMARY KEY (`locker_num`),
  UNIQUE INDEX `locker_num_UNIQUE` (`locker_num` ASC) VISIBLE)
ENGINE = InnoDB;

-- lockers 테이블 데이터 삽입
-- 1부터 20까지 TAG = 'B1'
-- 1부터 20까지 TAG = 'B1'
INSERT INTO lockers (locker_num, TAG)
VALUES 
    (1, 'B1'), (2, 'B1'), (3, 'B1'), (4, 'B1'), (5, 'B1'),
    (6, 'B1'), (7, 'B1'), (8, 'B1'), (9, 'B1'), (10, 'B1'),
    (11, 'B1'), (12, 'B1'), (13, 'B1'), (14, 'B1'), (15, 'B1'),
    (16, 'B1'), (17, 'B1'), (18, 'B1'), (19, 'B1'), (20, 'B1');

-- 21부터 90까지 TAG = '4F'
INSERT INTO lockers (locker_num, TAG)
VALUES 
    (21, '4F'), (22, '4F'), (23, '4F'), (24, '4F'), (25, '4F'),
    (26, '4F'), (27, '4F'), (28, '4F'), (29, '4F'), (30, '4F'),
    (31, '4F'), (32, '4F'), (33, '4F'), (34, '4F'), (35, '4F'),
    (36, '4F'), (37, '4F'), (38, '4F'), (39, '4F'), (40, '4F'),
    (41, '4F'), (42, '4F'), (43, '4F'), (44, '4F'), (45, '4F'),
    (46, '4F'), (47, '4F'), (48, '4F'), (49, '4F'), (50, '4F'),
    (51, '4F'), (52, '4F'), (53, '4F'), (54, '4F'), (55, '4F'),
    (56, '4F'), (57, '4F'), (58, '4F'), (59, '4F'), (60, '4F'),
    (61, '4F'), (62, '4F'), (63, '4F'), (64, '4F'), (65, '4F'),
    (66, '4F'), (67, '4F'), (68, '4F'), (69, '4F'), (70, '4F'),
    (71, '4F'), (72, '4F'), (73, '4F'), (74, '4F'), (75, '4F'),
    (76, '4F'), (77, '4F'), (78, '4F'), (79, '4F'), (80, '4F'),
    (81, '4F'), (82, '4F'), (83, '4F'), (84, '4F'), (85, '4F'),
    (86, '4F'), (87, '4F'), (88, '4F'), (89, '4F'), (90, '4F');


SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `locker`.`student`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `DB_Locks`.`student`;
CREATE TABLE IF NOT EXISTS `DB_Locks`.`student` (
  `student_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(8) NOT NULL,
  `department` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE INDEX `student_id_UNIQUE` (`student_id` ASC) VISIBLE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `locker`.`rent`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `DB_Locks`.`rent`;
CREATE TABLE IF NOT EXISTS `DB_Locks`.`rent` (
  `locker_num` INT UNSIGNED NOT NULL,
  `student_id` INT UNSIGNED NOT NULL,
  `rent_type` ENUM('long', 'short') NOT NULL,
  `date` DATE NOT NULL,
  `duration` INT UNSIGNED NOT NULL DEFAULT 3,
  PRIMARY KEY (`locker_num`),
  UNIQUE INDEX `locker_num_UNIQUE` (`locker_num` ASC) VISIBLE,
  UNIQUE INDEX `student_id_UNIQUE` (`student_id` ASC) VISIBLE,
  CONSTRAINT `locker_num`
    FOREIGN KEY (`locker_num`)
    REFERENCES `DB_Locks`.`lockers` (`locker_num`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `student_id`
    FOREIGN KEY (`student_id`)
    REFERENCES `DB_Locks`.`student` (`student_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `locker`.`log`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `DB_Locks`.`log`;
CREATE TABLE IF NOT EXISTS `DB_Locks`.`log` (
  `student_id` INT UNSIGNED NOT NULL,
  `date` DATE NOT NULL,
  `duration` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`student_id`),
  UNIQUE INDEX `student_id_UNIQUE` (`student_id` ASC) VISIBLE)
ENGINE = InnoDB;

SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
