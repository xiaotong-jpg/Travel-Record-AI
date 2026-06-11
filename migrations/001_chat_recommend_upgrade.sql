USE travel_memory;

ALTER TABLE travel_records
  ADD COLUMN source_type VARCHAR(20) NOT NULL DEFAULT 'form',
  ADD COLUMN chat_session_id VARCHAR(80) NULL,
  ADD COLUMN image_urls JSON NULL,
  ADD COLUMN hand_account_layout JSON NULL,
  ADD COLUMN exported_long_image_url VARCHAR(255) NULL;

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
