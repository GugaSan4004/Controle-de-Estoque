import os
import sqlite3

from pathlib import Path

class start:
    def __init__(self):        
        print("\n> Inicializando DataBase...")
        
        db_file = Path.cwd() / "modules" / "DBCore" / "db.sqlite"
        
        db_exists = db_file.exists()
        
        self.connector = sqlite3.connect(db_file, check_same_thread=False)
        
        if not db_exists:
            print(">> Banco não encontrado. Aplicando schema...")
            schema_file = Path.cwd() / "modules" / "DBCore" / "schema.sql"
            
            with open(schema_file, "r") as f:
                sql_schema = f.read()
            
            with self.connector:
                self.connector.executescript(sql_schema)
            
        self.connector.row_factory = sqlite3.Row
        
        __cur = self.connector.cursor()
        
        __cur.execute("PRAGMA table_info(movements);")
        self.movements_columns_names = [ dict(result).get("name") for result in __cur.fetchall() ]
        
        __cur.execute("PRAGMA table_info(stock);")
        self.stock_columns_names = [ dict(result).get("name") for result in __cur.fetchall() ]
        
        __cur.close()    
    
    def selectMovement(self, dateStart: str, dateEnd: str, ccFilter: str, fetchOne: bool = True) -> dict | None:
        cur = self.connector.cursor()

        ITEMS = {}

        cur.execute("SELECT id, name, unityType, unityPrice FROM stock WHERE place = 'ALMOX'")

        for item in cur.fetchall():
            item = dict(item)
            ITEMS[item["id"]] = {
                "name":       item["name"],
                "unityType":  item["unityType"],
                "unityPrice": item["unityPrice"],
            }

        # Map stock IDs to the column names used in the movements table
        FIELD_MAP = {
            1322: "hig",
            1323: "toa",
            1324: "sab",
        }

        # Pre-build grouped dict keyed by (id, name)
        grouped = {
            (item_id, meta["name"]): []
            for item_id, meta in ITEMS.items()
        }

        def transform(result: list) -> dict:
            """
            Converts flat DB movements into the grouped structure:
            {(item_id, name): [rows...]}
            """
            for mov in result:
                if mov["cc"] != ccFilter and (ccFilter != "TOTAL" or mov["cc"] == "COUNT"):
                    continue
                for item_id, meta in ITEMS.items():
                    col = FIELD_MAP.get(item_id)
                    if col is None:
                        continue
                    qty = mov.get(col, 0)
                    if qty == 0:
                        continue
                    grouped[(item_id, meta["name"])].append({
                        "id": mov["id"],
                        "quantity": qty,
                        "date": mov["date"],
                        "unityType": meta["unityType"],
                        "unityPrice": meta["unityPrice"],
                        "totalPrice": round(qty * meta["unityPrice"], 2),
                        "responsible": mov["responsible"].strip(),
                    })
                    # grouped[(item_id, meta["name"])].append({
                    #     "data_saida":     mov["date"],
                    #     "no_nota":        mov["id"],
                    #     "operador":       mov["responsible"].strip(),
                    #     "unidade":        meta["unityType"],
                    #     "quantidade":     qty,
                    #     "valor_unitario": meta["unityPrice"],
                    #     "total_linha":    qty * meta["unityPrice"],
                    # })
            return {k: v for k, v in grouped.items() if v}

        if ccFilter:
            cur.execute(
                f"""
                SELECT id, date, hig, toa, sab, responsible, cc
                FROM movements
                WHERE ('20' || substr(date,7,2) || '-' || substr(date,4,2) || '-' || substr(date,1,2))
                    BETWEEN ? AND ?
                """,
                (dateStart, dateEnd)
            )
        else:
            cur.execute(
                f"""
                SELECT id, date, hig, toa, sab, responsible, cc
                FROM movements
                WHERE cc = ?
                AND ('20' || substr(date,7,2) || '-' || substr(date,4,2) || '-' || substr(date,1,2))
                    BETWEEN ? AND ?
                """,
                (ccFilter, dateStart, dateEnd)
            )

        if not fetchOne:
            rows = [dict(row) for row in cur.fetchall()]
            result = transform(rows)
        else:
            row = cur.fetchone()
            result = transform([dict(row)]) if row else {}

        cur.close()

        return result if result else None
    
    def insertMovement(self, date: str, hig: int | float, toa: int | float, sab: int | float, responsible: str, cc: str, toUnderground: int):
        cur = self.connector.cursor()
        
        cur.execute(
            """
            INSERT INTO movements
                (date, hig, toa, sab, responsible, cc, toUnderground)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date,
                hig,
                toa,
                sab,
                responsible,
                cc,
                toUnderground,
            ),
        )
        
        self.connector.commit()
        
        cur.close()

    def inserPurchase(self, place: str, hig: int | float, toa: int | float, sab: int | float, received = None, shippingNoteId = None, date = None) -> bool:
        cur = self.connector.cursor()
        
        if place.upper() not in ["ALMOX", "R3"]:
            raise Exception("Local invalido!")
        
        if date:
            cur.execute("SELECT * FROM purchases WHERE toPlace = ? AND date = ?", (place, date))
            result = [dict(v) for v in cur.fetchall()]
            
            if len(result) > 0:
                return False
        
        cur.execute(
            """
            INSERT INTO purchases
                (toPlace, hig, toa, sab, received, shippingNoteId)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                place.upper(),
                hig,
                toa,
                sab,
                1 if place.upper() == "R3" else received,
                shippingNoteId
            ),
        )
        
        self.connector.commit()
        
        cur.close()
        
        return True
        
    def selectStock(self, place: str = "both") -> list[dict]:
        cur = self.connector.cursor()
        
        placeFilter = f"WHERE place = '{place.upper()}'" if place.upper() in ["R3", "ALMOX"] else ""
        
        cur.execute(f"SELECT * FROM stock {placeFilter}")
        result = [dict(result) for result in cur.fetchall()]
                
        cur.close()
        
        return result
    
    def matchShippingNote(self, noteId, hig: int | float, toa: int | float, sab: int | float) -> bool:
        cur = self.connector.cursor()
        
        cur.execute("SELECT * FROM purchases WHERE hig = ? AND toa = ? AND sab = ? AND received = 0", (hig, toa, sab))
        result = cur.fetchone()
        
        if result == None:
            return False
        
        cur.execute(f"SELECT id, quantity FROM stock")
        
        quantities = {
            "1212": 0,
            "1213": 0,
            "1214": 0,
            
            "1322": 0,
            "1323": 0,
            "1324": 0
        }
        
        for quantity in cur.fetchall():
            quantity = dict(quantity)
            quantities[quantity["id"]] = quantity["quantity"]
        
        cur.execute(f"UPDATE purchases SET received = 1, shippingNoteId = {noteId if noteId else 0} WHERE id = {dict(result).get("id")}")
        
        cur.execute(f"""
            UPDATE stock 
            SET quantity = CASE
                WHEN id = 1212 THEN {quantities["1212"] - hig}
                WHEN id = 1213 THEN {quantities["1213"] - toa}
                WHEN id = 1214 THEN {quantities["1214"] - sab}
                
                WHEN id = 1322 THEN {quantities["1322"] + hig}
                WHEN id = 1323 THEN {quantities["1323"] + toa}
                WHEN id = 1324 THEN {quantities["1324"] + sab}
            END;
        """)
        
        self.connector.commit()
        
        return True