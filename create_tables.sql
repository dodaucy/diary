CREATE TABLE IF NOT EXISTS `answers` (
    `days` MEDIUMINT UNSIGNED NOT NULL,
    `question_id` INT UNSIGNED NOT NULL,
    `value` TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (`days`, `question_id`)
);
CREATE TABLE IF NOT EXISTS `notes` (
	`days` MEDIUMINT UNSIGNED NOT NULL,
	`notes` TEXT NOT NULL,
	PRIMARY KEY (`days`)
);
CREATE TABLE IF NOT EXISTS `questions` (
	`id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
	`name` TINYTEXT NOT NULL,
	`color` VARCHAR(7) NOT NULL,
	PRIMARY KEY (`id`)
);
CREATE TABLE IF NOT EXISTS `sessions` (
	`token` CHAR(64) NOT NULL,
	`last_request` INT NOT NULL,
	`created_at` INT NOT NULL,
	PRIMARY KEY (`token`)
);
CREATE TABLE IF NOT EXISTS `settings` (
	`font_color` VARCHAR(7) NOT NULL,
	`button_font_color` VARCHAR(7) NOT NULL,
	`primary_background_color` VARCHAR(7) NOT NULL,
	`secondary_background_color` VARCHAR(7) NOT NULL,
	`navbar_selected_item_color` VARCHAR(7) NOT NULL,
	`font_family` VARCHAR(32) NOT NULL
);
