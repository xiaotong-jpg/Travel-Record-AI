CREATE DATABASE IF NOT EXISTS travel_memory
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE travel_memory;

CREATE TABLE IF NOT EXISTS travel_records (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  place VARCHAR(120) NOT NULL,
  travel_date DATE NOT NULL,
  companion VARCHAR(120) NULL,
  mood VARCHAR(80) NULL,
  memory TEXT NOT NULL,
  quote VARCHAR(255) NULL,
  style VARCHAR(40) NOT NULL,
  title VARCHAR(160) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  location_desc TEXT NULL,
  mood_tags JSON NULL,
  stickers JSON NULL,
  share_text TEXT NULL,
  source_type VARCHAR(20) NOT NULL DEFAULT 'form',
  chat_session_id VARCHAR(80) NULL,
  image_urls JSON NULL,
  hand_account_layout JSON NULL,
  exported_long_image_url VARCHAR(255) NULL,
  raw_ai_response MEDIUMTEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_created_at (created_at),
  INDEX idx_travel_date (travel_date),
  INDEX idx_place (place)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chat_sessions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  session_id VARCHAR(80) NOT NULL,
  messages_json JSON NOT NULL,
  travel_info_json JSON NOT NULL,
  uploaded_images_json JSON NULL,
  finished TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recommendations (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  city VARCHAR(80) NULL,
  current_place VARCHAR(120) NULL,
  latitude DOUBLE NULL,
  longitude DOUBLE NULL,
  preferences_json JSON NULL,
  visited_places_json JSON NULL,
  poi_json JSON NULL,
  result_json JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_city_place (city, current_place)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
