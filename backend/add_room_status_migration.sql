-- Migration: Add status column to room table
-- Run this in your PostgreSQL database

ALTER TABLE room 
ADD COLUMN IF NOT EXISTS status BOOLEAN NOT NULL DEFAULT true;

-- Update any existing rooms to be available by default
UPDATE room SET status = true WHERE status IS NULL;

-- Verify the migration
SELECT id, name, status FROM room LIMIT 5;
