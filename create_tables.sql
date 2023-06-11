CREATE TABLE IF NOT EXISTS `answers` (
    `days` MEDIUMINT(8) UNSIGNED NOT NULL,
    `question_id` INT(10) UNSIGNED NOT NULL,
    `value` TINYINT(3) UNSIGNED NOT NULL,
    PRIMARY KEY (`days`, `question_id`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
;
CREATE TABLE IF NOT EXISTS `notes` (
	`days` MEDIUMINT(8) UNSIGNED NOT NULL,
	`notes` TEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	PRIMARY KEY (`days`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
;
CREATE TABLE IF NOT EXISTS `questions` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`name` TINYTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	`color` VARCHAR(7) NOT NULL COLLATE 'utf8mb4_general_ci',
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
;
CREATE TABLE IF NOT EXISTS `sessions` (
	`token` CHAR(64) NOT NULL COLLATE 'utf8mb4_general_ci',
	`last_request` INT(11) NOT NULL,
	`created_at` INT(11) NOT NULL,
	PRIMARY KEY (`token`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
;
CREATE TABLE IF NOT EXISTS `settings` (
	`font_color` VARCHAR(7) NOT NULL COLLATE 'utf8mb4_general_ci',
	`button_font_color` VARCHAR(7) NOT NULL COLLATE 'utf8mb4_general_ci',
	`primary_background_color` VARCHAR(7) NOT NULL COLLATE 'utf8mb4_general_ci',
	`secondary_background_color` VARCHAR(7) NOT NULL COLLATE 'utf8mb4_general_ci',
	`navbar_selected_item_color` VARCHAR(7) NOT NULL COLLATE 'utf8mb4_general_ci',
	`font_family` VARCHAR(32) NOT NULL COLLATE 'utf8mb4_general_ci'
)
COLLATE='utf8mb4_general_ci'
;
