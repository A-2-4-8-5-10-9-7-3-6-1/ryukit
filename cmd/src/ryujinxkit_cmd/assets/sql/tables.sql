-- ============================================================================

CREATE TABLE IF NOT EXISTS saves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag VARCHAR(20) DEFAULT untagged,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
