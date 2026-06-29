-- ==============================================================
-- VALIDATED & CORRECTED SCHEMA + WORKFLOW TRIGGERS
-- SQLite
-- ==============================================================
-- IMPORTANT: run this PRAGMA at the start of every connection
-- so that foreign-key constraints are actually enforced.
PRAGMA foreign_keys = ON;


-- ==============================================================
-- SCHEMA
-- ==============================================================

-- -------------------------------------------------------------
-- items
-- Changes vs original:
--   • Unified quoting style to double-quotes (SQL standard)
--   • place: added NOT NULL (it has a sensible default 'ALMOX')
--   • minimum, ideal: added NOT NULL (both already have DEFAULT 0)
--   • CHECK guards added: quantity, unityPrice, minimum, ideal ≥ 0
-- -------------------------------------------------------------
CREATE TABLE "items" (
  "id"         INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "name"       TEXT,
  "place"      TEXT NOT NULL DEFAULT 'ALMOX',
  "unityType"  TEXT,
  "unityPrice" INTEGER NOT NULL DEFAULT 0,
  "quantity"   INTEGER NOT NULL DEFAULT 0,
  "minimum"    INTEGER NOT NULL DEFAULT 0,
  "ideal"      INTEGER NOT NULL DEFAULT 0,
  "category"   TEXT,
  CHECK ("quantity"   >= 0),
  CHECK ("unityPrice" >= 0),
  CHECK ("minimum"    >= 0),
  CHECK ("ideal"      >= 0)
);

-- -------------------------------------------------------------
-- movements
-- Changes vs original:
--   • Unified quoting style
--   • Removed duplicate UNIQUE on PK (PRIMARY KEY is already unique)
-- -------------------------------------------------------------
CREATE TABLE "movements" (
  "id"          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "date"        TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "responsible" TEXT NOT NULL,
  "locale"      TEXT,
  "cc"          TEXT NOT NULL
);

-- -------------------------------------------------------------
-- movements_items
-- Changes vs original:
--   • Removed duplicate UNIQUE on PK
--   • quantity: added DEFAULT 0
--   • CHECK quantity > 0 (a zero-quantity movement line makes no sense)
--   • FK: added ON DELETE RESTRICT ON UPDATE CASCADE for integrity
-- -------------------------------------------------------------
CREATE TABLE "movements_items" (
  "id"          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "movementsId" INTEGER NOT NULL REFERENCES "movements"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
  "itemsId"     INTEGER NOT NULL REFERENCES "items"("id")     ON DELETE RESTRICT ON UPDATE CASCADE,
  "quantity"    INTEGER NOT NULL DEFAULT 0,
  CHECK ("quantity" > 0)
);

-- -------------------------------------------------------------
-- purchases
-- Changes vs original:
--   • Added NOT NULL to id (PK is implicitly not null, made explicit)
--   • date: added NOT NULL (has a default, so safe)
--   • CHECK received IN (0,1) — enforces boolean semantics
-- -------------------------------------------------------------
CREATE TABLE "purchases" (
  "id"             INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "date"           TEXT NOT NULL DEFAULT (CURRENT_DATE),
  "received"       INTEGER NOT NULL DEFAULT 0,
  "shippingNoteId" INTEGER DEFAULT NULL,
  CHECK ("received" IN (0, 1))
);

-- -------------------------------------------------------------
-- purchases_items
-- Changes vs original:
--   • Renamed "itemId" → "itemsId" (consistent with movements_items)
--   • Removed duplicate UNIQUE on PK
--   • quantity: fixed DEFAULT 0.0 → DEFAULT 0 (column is INTEGER)
--   • CHECK quantity > 0
--   • FK: added ON DELETE RESTRICT ON UPDATE CASCADE for integrity
-- -------------------------------------------------------------
CREATE TABLE "purchases_items" (
  "id"          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "itemsId"     INTEGER NOT NULL REFERENCES "items"("id")     ON DELETE RESTRICT ON UPDATE CASCADE,
  "purchasesId" INTEGER NOT NULL REFERENCES "purchases"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
  "quantity"    INTEGER NOT NULL DEFAULT 0,
  CHECK ("quantity" > 0)
);


-- ==============================================================
-- TRIGGERS
-- ==============================================================

-- --------------------------------------------------------------
-- RULE 1 — movements_items INSERT
-- Subtract the new quantity from the referenced item's stock.
-- --------------------------------------------------------------
CREATE TRIGGER trg_movements_items_after_insert
AFTER INSERT ON "movements_items"
FOR EACH ROW
BEGIN
  UPDATE "items"
  SET    "quantity" = "quantity" - NEW."quantity"
  WHERE  "id" = NEW."itemsId";
END;

-- --------------------------------------------------------------
-- RULE 2 — movements_items UPDATE
-- Roll back the old quantity (add it back) and subtract the new
-- quantity, effectively replacing the previous stock deduction.
-- --------------------------------------------------------------
CREATE TRIGGER trg_movements_items_after_update
AFTER UPDATE ON "movements_items"
FOR EACH ROW
BEGIN
  UPDATE "items"
  SET    "quantity" = "quantity" + OLD."quantity" - NEW."quantity"
  WHERE  "id" = NEW."itemsId";
END;

-- --------------------------------------------------------------
-- RULE 3 — purchases_items INSERT
-- Add the new quantity to the referenced item's stock.
-- --------------------------------------------------------------
CREATE TRIGGER trg_purchases_items_after_insert
AFTER INSERT ON "purchases_items"
FOR EACH ROW
BEGIN
  UPDATE "items"
  SET    "quantity" = "quantity" + NEW."quantity"
  WHERE  "id" = NEW."itemsId";
END;

-- --------------------------------------------------------------
-- RULE 4 — purchases_items UPDATE
-- Roll back the old quantity (subtract it) and add the new
-- quantity, replacing the previous stock addition.
-- --------------------------------------------------------------
CREATE TRIGGER trg_purchases_items_after_update
AFTER UPDATE ON "purchases_items"
FOR EACH ROW
BEGIN
  UPDATE "items"
  SET    "quantity" = "quantity" - OLD."quantity" + NEW."quantity"
  WHERE  "id" = NEW."itemsId";
END;