import os
import re
import time
import base64
import requests

from pathlib import Path
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from modules.console_manager import *
from reportlab.lib.pagesizes import A4


PAGE_W, PAGE_H = A4
LEFT = 15 * mm
RIGHT = PAGE_W - 15 * mm
COL_DATA = LEFT
COL_NOTA = LEFT + 22 * mm
COL_UNID = LEFT + 50 * mm
COL_QTD = LEFT + 68 * mm
COL_UNIT = LEFT + 100 * mm
COL_TOTAL = LEFT + 132 * mm

FONT_NORMAL = "Courier"
FONT_BOLD = "Courier-Bold"
FONT_SEMIBOLD = "Courier-BoldOblique"

SIZE_EXBIG = 11
SIZE_BIG = 10
SIZE_NORMAL = 9

LINE_H = 4 * mm
TAB = "         "
TAB_LENGTH = 9

LINE_WIDTH = 0.5

TYPE_DICT = {
    "BOX": "CAIXA",
    "ROL": "ROLO",
    "GAL": "GALÃO"
}

class start:
    def __init__(self) -> None:
        printf("Inicializando manipulador de PDF...")
        
        self.BUSINESS = "MAIA E BORBA S/A"
        self.SYSTEM = "Sistema de Higiênicos"

        self.y = 0.0
        self.page_num = 0
        
        self.output_path = Path.cwd() / "modules" / "PDFManipulator" / "pdf_files"
        
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
            
        if os.path.exists(self.output_path / "resume_temp.pdf"):
            os.remove(self.output_path / "resume_temp.pdf")
        
        self.canva = canvas.Canvas(str(self.output_path / "resume_temp.pdf"), pagesize=A4)
        
        self.start_date: str
        self.finish_date: str
        self.movement_type: str
        self.filter_by: str | None
        
        time.sleep(1)

    def __new_page(self):
        if self.page_num > 0:
            self.canva.showPage()
        self.page_num += 1
        self.y = PAGE_H - 10 * mm
        self.__header()

    def __header(self):
        c = self.canva
        periodo = (f"no Período de {self.start_date} "
                   f"a {self.finish_date}")
        today = date.today().strftime("%d/%m/%Y")

        c.setLineWidth(LINE_WIDTH + 0.5)
        c.line(LEFT, self.y, RIGHT, self.y)
        self.y -= LINE_H
        
        c.setFont(FONT_NORMAL, SIZE_NORMAL)
        c.drawRightString(RIGHT, self.y, today)
        self.y -= LINE_H
        
        c.drawString(LEFT, self.y, self.SYSTEM)
        c.drawRightString(RIGHT, self.y, f"Página {self.page_num}")
        self.y -= LINE_H
 
        c.setFont(FONT_BOLD, SIZE_NORMAL)
        c.drawCentredString(PAGE_W / 2, self.y, f"{self.movement_type}{" por Centro de Custo" if self.filter_by else ""} {periodo}")
        self.y -= LINE_H
 
        c.setLineWidth(LINE_WIDTH + 0.5)
        c.line(LEFT, self.y, RIGHT, self.y)
        self.y -= LINE_H
 
        if self.filter_by != None and self.filter_by != "":
            c.setFont(FONT_BOLD, SIZE_EXBIG)
            c.drawString(LEFT, self.y, f"CC: {self.filter_by} - CONSERVAÇÃO E LIMPEZA")
            self.y -= LINE_H * 1.6
            
        self.y -= LINE_H * 2
            
    def __check_spaces(self, lines=2):
        if self.y < 6 * mm + lines * LINE_H:
            self.__new_page()
            
    def __footer(self):
        c = self.canva
        c.setFont(FONT_NORMAL, SIZE_NORMAL)
        c.drawString(LEFT, 10 * mm, self.BUSINESS)

    def __set_underline_text(self, text: str, style: str, size: float):
        c = self.canva
        import re

        full_text_width = c.stringWidth(text, style, size)
        text_start_x = PAGE_W / 2 - full_text_width / 2 

        c.setLineWidth(LINE_WIDTH + 0.5)
        
        words_and_spaces = re.split(r'(\s+)', text)
        
        current_x = text_start_x
        
        for item in words_and_spaces:
            item_width = c.stringWidth(item, style, size)
            
            if not re.match(r'^\s{2,}$', item) and not item.isspace(): 
                line_end_x = current_x + item_width
                c.line(current_x, self.y - 0.8 * mm, line_end_x, self.y - 0.8 * mm)
            
            elif len(item) == 1 and item == " ":
                line_end_x = current_x + item_width
                c.line(current_x, self.y - 0.8 * mm, line_end_x, self.y - 0.8 * mm)
                
            current_x += item_width
        
    def __item_header(self, no_item: str, descricao: str):
        self.__check_spaces(4)
        c = self.canva
            
        no_text = f"No.: {no_item}"
        
        full_text = descricao + TAB + no_text
        
        c.setFont(FONT_BOLD, SIZE_BIG)
        self.__set_underline_text(full_text, FONT_BOLD, SIZE_BIG)
        c.drawCentredString(PAGE_W / 2, self.y, full_text)

        self.y -= LINE_H + 2 * mm

        c.setFont(FONT_NORMAL, SIZE_NORMAL)
        c.drawString(LEFT, self.y, f"Data     No. Nota         Unid.        "
                                    f"Quantidade    Valor Unitário                 Valor Total")
        self.y -= LINE_H * 0.4
        c.setLineWidth(LINE_WIDTH)
        c.line(LEFT, self.y, RIGHT, self.y)
        self.y -= LINE_H
        
    def __movement_line(self, row: dict):
        self.__check_spaces()
        c = self.canva
        
        c.setFont(FONT_NORMAL, SIZE_NORMAL)
 
        data_fmt = row["date"]
        qtd_fmt  = f"{row['quantity']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        unit_fmt = f"{row['unityPrice']:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tot_fmt  = f"{row['totalPrice']:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
 
        c.drawString(COL_DATA,  self.y, data_fmt)
        c.drawString(COL_NOTA,  self.y, str(row["id"]))
        c.drawString(COL_UNID,  self.y, TYPE_DICT[row["unityType"]])
        c.drawRightString(COL_QTD  + 22 * mm, self.y, qtd_fmt)
        c.drawRightString(COL_UNIT + 22 * mm, self.y, unit_fmt)
        c.drawRightString(RIGHT, self.y, tot_fmt)
        self.y -= LINE_H

        arrow_x = LEFT + 1 * mm
        arrow_top = self.y + LINE_H * 0.8
        arrow_mid = self.y + LINE_H * 0.3

        c.setLineWidth(LINE_WIDTH)

        c.line(arrow_x, arrow_top, arrow_x, arrow_mid)

        c.line(arrow_x, arrow_mid, arrow_x + 2 * mm, arrow_mid)

        tip_x = arrow_x + 2 * mm
        c.line(tip_x, arrow_mid + 0.8 * mm, tip_x + 1.5 * mm, arrow_mid)
        c.line(tip_x, arrow_mid - 0.8 * mm, tip_x + 1.5 * mm, arrow_mid)
    
        c.setFont(FONT_NORMAL, SIZE_NORMAL)
        c.drawString(arrow_x + 4.5 * mm, arrow_mid - 0.7 * mm, f"Responsável: {row['responsible']}")
        
        self.y -= LINE_H * 1.6

    def __total_item(self, total_qtd: float, total_val: float):
        self.__check_spaces()
        c = self.canva
 
        qtd_fmt = f"{total_qtd:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        val_fmt = f"{total_val:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
 
        c.setLineWidth(LINE_WIDTH)
        c.line(LEFT, self.y + LINE_H * 0.7, RIGHT, self.y + LINE_H * 0.7)
 
        self.y -= LINE_H * 0.5
        
        c.setFont(FONT_BOLD, SIZE_NORMAL)
        c.drawString(LEFT, self.y, f"Total do Item: ")
        c.drawRightString(COL_QTD  + 22 * mm, self.y, qtd_fmt)
        c.drawRightString(RIGHT, self.y, val_fmt)
        self.y -= LINE_H * 2.5

    def __total_cc(self, total_items: dict):
        self.__new_page()
        c = self.canva
        
        totalGeneral = 0.0
        totalPrice = 0.0
        
        for (item, values) in total_items.items():
            full_text = item + TAB + f"No.: {values['id']}"
            
            self.__set_underline_text(full_text, FONT_BOLD, SIZE_BIG)
            
            c.setFont(FONT_SEMIBOLD, SIZE_BIG)
            c.drawCentredString(PAGE_W / 2, self.y, full_text)
            self.y -= LINE_H * 1.4
            
            c.setFont(FONT_NORMAL, SIZE_NORMAL)
            c.drawRightString(RIGHT, self.y, "Quantidade Total" + TAB * 2 + "Valor Total")
            self.y -= LINE_H * 1.4
            
            c.setFont(FONT_BOLD, SIZE_NORMAL)
            c.drawRightString(RIGHT, self.y, 
                f"{values["totalUnity"]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + 
                TAB * 2 +
                f"{values["totalPrice"]:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.y -= LINE_H * 1.2
            
            c.setLineWidth(LINE_WIDTH)
            c.line(LEFT, self.y, RIGHT, self.y)
            self.y -= LINE_H * 1.8
            
            totalGeneral += values["totalUnity"]
            totalPrice += values["totalPrice"]
            
        c.setFont(FONT_NORMAL, SIZE_NORMAL)
        c.drawRightString(RIGHT, self.y, "Quantidade Total Geral" + TAB * 2 + "Valor Total Geral")
        self.y -= LINE_H * 1.4
        
        c.setFont(FONT_BOLD, SIZE_NORMAL)
        c.drawRightString(RIGHT, self.y, f"{totalGeneral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + TAB * 3 + f"{totalPrice:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.y -= LINE_H * 1.2

    def generateReport(self, values: dict, start_date: str, finish_date: str, movement_type: str, filter_by: str = "TOTAL"):
        printf(f"Gerando relatorio '{filter_by}'...")
        
        if self.canva == None:
            self.canva = canvas.Canvas(str(self.output_path / "resume_temp.pdf"), pagesize=A4)
            
        self.start_date = start_date
        self.finish_date = finish_date
        self.movement_type = movement_type
        self.filter_by = filter_by if filter_by != "TOTAL" else None
                
        total_items = {}
        
        for (no_item, descricao), linhas in values.items():
            self.__item_header(no_item, descricao)
 
            total_items[descricao] = {
                "id": no_item,
                "totalUnity": 0,
                "totalPrice": 0
            }
            
            total_item_qtd = 0.0
            total_item_val = 0.0
 
            for row in linhas:
                self.__movement_line(row)
                total_item_qtd += row["quantity"]
                total_item_val += row["totalPrice"]

            total_items[descricao]["totalUnity"] = total_item_qtd
            total_items[descricao]["totalPrice"] = total_item_val
            
            self.__total_item(total_item_qtd, total_item_val)
 
        self.__total_cc(total_items)
        self.__footer()
        
        self.canva.save()
        
        if not self.filter_by: self.filter_by = 'Total'
        
        if os.path.exists(self.output_path / f"Relatorio de Higiênicos - {self.filter_by}"):
            os.remove(self.output_path / f"Relatorio de Higiênicos - {self.filter_by}")
        
        Path.move(
            self.output_path / "resume_temp.pdf", 
            self.output_path / f"Relatorio de Higiênicos - {self.filter_by if self.filter_by else 'Total'}.pdf" 
        )
        
        self.canva = None
        self.y = 0.0
        self.page_num = 0
        
        warning(f"Relatório '{self.movement_type} - {self.filter_by}' gerado com sucesso!")
        
        return {
            {1322: "hig", 1323: "toa", 1324: "sab"}[data["id"]]: {**{k: v for k, v in data.items()}}
            for _, data in total_items.items()
        }
    
    def getDanfes(self, danfe_key: str):
        clean_key = re.sub(r"\D", "", danfe_key)
        
        if len(clean_key) != 44:
            raise ValueError(f"Invalid key! Expected 44 digits, got {len(clean_key)} digits.")

        printf(f"Requisitando DANFE utilizando a chave: {clean_key}...")
        response = requests.post(
            'https://consultadanfe.com/api/v1/consulta',
            json={'chave': clean_key}
        )
        
        if response.status_code == 200:
            pdf_bytes = base64.b64decode(response.json()['pdf_base64'])
            with open(rf"modules\PDFManipulator\nfs\NF - {clean_key[25:34]} key - {clean_key}.pdf", "wb") as f:
                f.write(pdf_bytes)
            success(f">> Nota Fiscal {clean_key[25:34]} salva com sucesso!")
            return True
        else:
            response = response.json()
            raise Exception(f"Falha no download da NF -> {response.get("error", "Error Desconhecido: ")} {response.get("message", "unknown error!")}")