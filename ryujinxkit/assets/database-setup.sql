------------------------
-- Database Setup Script
------------------------
CREATE TABLE IF NOT EXISTS saves (
  id INTEGER PRIMARY KEY,
  tag VARCHAR(20) DEFAULT 'untagged' NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  used TIMESTAMP,
  size INTEGER DEFAULT 0 NOT NULL
);

CREATE TRIGGER IF NOT EXISTS update_save_updated_timestamp BEFORE
UPDATE ON saves FOR EACH ROW BEGIN
UPDATE saves
SET
  updated = CURRENT_TIMESTAMP
WHERE
  id = OLD.id;

END;
