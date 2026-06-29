import re
import os
import time
import base64
import locale
import datetime
import tempfile

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")

class start:
    def __init__(self, Timeout: int, FullScreen: bool = False):
        tried: int = 0
        
        print("> Inicializando Webmail... [ Esse processo pode demorar um pouco... ]")
        
        
        WEBSITE = os.getenv("EMAIL_WEBSITE")
        EMAIL = os.getenv("EMAIL_USER")
        PASSWORD = os.getenv("EMAIL_PASSWORD")
        
        os.environ["SE_OFFLINE"] = "true"
        
        if not WEBSITE or not EMAIL or not PASSWORD:
            raise Exception("Environement not set!")
        
        while tried >= 0:
            try:
                options = Options()
                options.add_argument("--headless") if not FullScreen else options.add_argument("--full-screen")
                
                options.binary_location = r"C:\Users\ar.almoxarifado\AppData\Local\Mozilla Firefox\firefox.exe"
                options.profile = r"C:\Users\ar.almoxarifado\AppData\Roaming\Mozilla\Firefox\Profiles\ykylgi0j.Bot"

                driver = webdriver.Firefox(options=options)
                            
                driver.get(WEBSITE)
                
                wait: WebDriverWait[WebDriver] = WebDriverWait(driver, Timeout)
                
                time.sleep(2)
                
                wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
                wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
                wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
            
                if FullScreen:
                    driver.set_window_position(-1024, -12)
                    time.sleep(1)
                    driver.fullscreen_window()
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception as e:
                tried += 1
                
                if tried >= 3:
                    print(f"\n>>> Error ao logar... Tentativas Excedidas... ({tried})\n\nError -> {e}")
                    if driver:
                        driver.quit()
                    raise Exception(e)
                else:
                    print(f"\n>> Error ao logar... Tentando novamente... ({tried}º)")
                    time.sleep(5)
            else:
                tried = -1
                self.driver = driver
                self.wait = wait
          
    def fetchEmail(self, targetEmail: str, place: str = "receive"):
        Path_main = ""
        Path_alternative = ""
        
        if "parreira" in targetEmail.lower():
            print("\n> Extraindo Email de \"Parreira\"...")
        elif "edielson" in targetEmail.lower():
            print("\n> Extraindo Email de \"Edielson\"...")
      
        if "sent" in place:
            Path_main = "//span[contains(text(), 'Enviado')]"
            Path_alternative = "[data-qtip='Enviado']"
        elif "receive" in place:
            Path_main = "//span[contains(text(), 'Caixa de entrada')]"
            Path_alternative = "[data-qtip='Caixa de entrada']"

        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, Path_main))).click()
        except:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, Path_alternative))).click()

        to_field = self.wait.until(EC.presence_of_element_located((By.ID, "quicksearchcombobox-1060-inputEl")))
        to_field.send_keys(targetEmail)
        to_field.send_keys(Keys.RETURN)

        time.sleep(2)
                
        return self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "email-body"))).text

    def sendEmail(self, template, dest: list, copy: list | None = None, **kwargs) -> bool:
        print("\n> Preparando o Email ( Etapa Final )...")

        titleMessage = ""
        
        if template.lower() == "shipment":
            titleMessage = "Pedido de Higiênicos"
            now = datetime.datetime.now()
            tomorrow = now + datetime.timedelta(days=1)
            templateFile = "PedidoEmail_template.html"
            
            calendar = {
                "Monday": "Segunda Feira",
                "Tuesday": "Terça Feira",
                "Wednesday": "Quarta Feira",
                "Thursday": "Quinta Feira",
                "Friday": "Sexta Feira"
            }
            
            stockNeeded = kwargs.get("stockNeeded")
            actualStock = kwargs.get("actualStock")
            
            if not stockNeeded or not actualStock:
                raise Exception("Values not passed!")
            values = {
                "talktime": "Boa tarde" if now.hour >= 13 else "Bom dia",
                "weekday": calendar[tomorrow.strftime('%A')],
                "dateship": tomorrow.strftime('%d/%m/%Y'),
                
                "higout": "{:.2f}".format(stockNeeded["HIG"]),
                "toaout": "{:.2f}".format(stockNeeded["TOA"]),
                "sabout": "{:.2f}".format(stockNeeded["SAB"]),

                "hignow": "{:.2f}".format(actualStock["R3"]["HIG"] - stockNeeded["HIG"]),
                "toanow": "{:.2f}".format(actualStock["R3"]["TOA"] - stockNeeded["TOA"]),
                "sabnow": "{:.2f}".format(actualStock["R3"]["SAB"] - stockNeeded["SAB"]),
            }
        elif template.lower() == "report":
            templateFile = "RelatorioEmail_template.html"
            start_date = kwargs.get("startDate")
            stockTotal = kwargs.get("stockTotal")
            finish_date = kwargs.get("finishDate")
            reportValues = kwargs.get("reportValues")

            if not reportValues or not start_date or not finish_date or not stockTotal:
                raise Exception("Values not passed!")
            
            hig_total_unity = reportValues["TOTAL"]["hig"]["totalUnity"]
            toa_total_unity = reportValues["TOTAL"]["toa"]["totalUnity"]
            sab_total_unity = reportValues["TOTAL"]["sab"]["totalUnity"]

            hig_total_price = reportValues["TOTAL"]["hig"]["totalPrice"]
            toa_total_price = reportValues["TOTAL"]["toa"]["totalPrice"]
            sab_total_price = reportValues["TOTAL"]["sab"]["totalPrice"]
            
            def fmt_currency(value: float) -> str:
                return f"R$ {value:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")

            def fmt_qty(value: float, decimals: int = 2) -> str:
                return f"{value:.{decimals}f}"

            def calc_total(mov: dict, cc: str) -> float:
                return sum(
                    mov[cc][item]["totalPrice"]
                    for item in ("hig", "toa", "sab")
                )

            def build_cc_values(mov: dict, cc: str, prefix: str) -> dict:
                hig = mov[cc]["hig"]
                toa = mov[cc]["toa"]
                sab = mov[cc]["sab"]

                return {
                    f"ph{prefix}cx":   fmt_qty(hig["totalUnity"]),        # caixas
                    f"ph{prefix}rl":   fmt_qty(hig["totalUnity"] * 8),             # rolos
                    f"valph{prefix}":  fmt_currency(hig["totalPrice"]),

                    f"pt{prefix}cx":   fmt_qty(toa["totalUnity"] / 6),
                    f"pt{prefix}rl":   fmt_qty(toa["totalUnity"]),
                    f"valpt{prefix}":  fmt_currency(toa["totalPrice"]),

                    f"s{prefix}cx":    fmt_qty(sab["totalUnity"] / 2),
                    f"s{prefix}gl":    fmt_qty(sab["totalUnity"]),
                    f"vals{prefix}":   fmt_currency(sab["totalPrice"]),

                    f"valtt{prefix}":  fmt_currency(calc_total(mov, cc)),
                }
                
            values = {
                "month": start_date.strftime("%B").title(),
                "date1": start_date.strftime("%d/%m/%Y"),
                "date2": finish_date.strftime("%d/%m/%Y"),

                **build_cc_values(reportValues, "COMLI", "a"),
                **build_cc_values(reportValues, "TR1", "tr"),

                # totals
                "phtsc":   fmt_qty(hig_total_unity),
                "phtsrl":  fmt_qty(hig_total_unity * 8),
                "valphtt": fmt_currency(hig_total_price),

                "pttsc":   fmt_qty(toa_total_unity / 6),
                "pttsrl":  fmt_qty(toa_total_unity),
                "valpttt": fmt_currency(toa_total_price),

                "stsc":    fmt_qty(sab_total_unity / 2),
                "stsgl":   fmt_qty(sab_total_unity),
                "valstt":  fmt_currency(sab_total_price),

                "valtt":   fmt_currency(
                    hig_total_price +
                    toa_total_price +
                    sab_total_price
                ),
                
                "eahigc": f"{stockTotal["hig"]:.2f}",
                "eahigrl": f"{stockTotal["hig"]*8:.2f}",
            
                "eatoc": f"{stockTotal["toa"]:.2f}",
                "eator": f"{stockTotal["toa"]*6:.2f}",

                "easab": f"{stockTotal["sab"]/2:.2f}",
                "easab2": f"{stockTotal["sab"]:.2f}",
            }
                                    
            titleMessage = f"Relatório de Higiênicos | {values.get('month','')}"
        else:
            raise Exception("Template not found!")

        time.sleep(4)
        
        self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//span[contains(text(),'Escrever')] | //span[contains(text(),'Novo')] | //span[contains(text(),'Redigir')] | //span[contains(text(),'Compor')]"
            ))
        ).click()

        for to in dest:
            self.wait.until(EC.presence_of_element_located((By.ID, "mailfieldcombo-1181-inputEl"))).send_keys(to)
            time.sleep(0.4)

        for cc in copy if copy else []:
            self.wait.until(EC.presence_of_element_located((By.ID, "mailfieldcombo-1186-inputEl"))).send_keys(cc)
            time.sleep(0.4)

        title = self.wait.until(EC.presence_of_element_located((By.ID, "textfield-1194-inputEl")))
        
        title.send_keys(titleMessage)
        
        SIGNATURE = ""
        HTML_TEMPLATE = ""
        
        with open(Path.cwd() /  "modules" / "WebmailCore" / templateFile, 'r', encoding='utf-8') as file:
            HTML_TEMPLATE = file.read()
        
        if os.path.exists(Path.cwd() /  "modules" / "WebmailCore" / "att.png"):
            with open(Path.cwd() /  "modules" / "WebmailCore" / "att.png", 'rb') as img_file:
                SIGNATURE = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            print(">> Alerta - Imagem de assinatura não encontrada! Ignorando essa etapa...")
        
        html_content = HTML_TEMPLATE.replace("cid:assinatura_logo", f"data:image/png;base64,{SIGNATURE}")
        
        for k, v in values.items():
            html_content = html_content.replace("{{" + k + "}}", str(v))

        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            self.driver.switch_to.frame(iframes[0])
            
        time.sleep(0.8)
        editable = self.driver.find_element(By.XPATH, "//body[@contenteditable='true']")
        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", editable, html_content)

        self.driver.switch_to.default_content()

        if template.lower() == "report":
            pdfFolder = Path.cwd() / "modules" / "PDFManipulator" / "pdf_files"
            
            for fn in os.listdir(pdfFolder):
                if fn.endswith('.pdf') and '.ignore' not in fn.lower():
                    file_path = os.path.join(pdfFolder, fn)
                    self.driver.find_element(By.XPATH, "//input[@type='file']").send_keys(file_path)
                    time.sleep(0.5)
        
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            file_path = f.name
        
        response = "y" if kwargs.get("autoYArgs") else input("\n>> Confira as informações do email na pré-visualização\n\n[Y] para enviar o email ou qualquer outra tecla para cancelar o envio\n\nComando [Y]>").lower()
        if response.lower() in ["y", "", None]:
            self.wait.until(EC.element_to_be_clickable((By.ID, "webmailbutton-1161-btnEl"))).click()
            
            print("\n>> Email enviado com sucesso!")
            time.sleep(5)
            
            os.unlink(file_path)
            return True
        else:
            print("\n>> Envio cancelado!")
            
            self.wait.until(EC.element_to_be_clickable((By.ID, "webmailbutton-1175-btnEl"))).click()
            time.sleep(1)
            
            self.wait.until(EC.element_to_be_clickable((By.ID, "webmailbutton-1048-btnEl"))).click()
            time.sleep(5)
            
            os.unlink(file_path)
            return False
        
    def extractValues(self, emailContent: str, template: str) -> dict | None:
        match template.lower():
            case "edielson":
                Actual_centro = ""
                Actual_item = ""
                Value_found = False
                
                email_date_match = re.search(r"referente ao mês de\s*([0-9]{1,2}|[A-Za-zÀ-ÿ]+)\s*/\s*(\d{4})", emailContent, re.IGNORECASE)
                
                values = {
                    "COMLI": {
                        "HIG": 0.0,
                        "TOA": 0.0,
                        "SAB": 0.0
                    },
                    "TR1": {
                        "HIG": 0.0,
                        "TOA": 0.0,
                        "SAB": 0.0
                    },
                    "EMAILDATE": ""
                }
                
                if not email_date_match:
                    raise Exception("O email mudou de formato, favor verificar o mesmo e alterar as variaveis do codigo!")

                try:
                    month_part = email_date_match.group(1).strip()
                    year_part = int(email_date_match.group(2))
                    month_num = None

                    if month_part.isdigit():
                        month_num = int(month_part)
                    else:
                        months_map = {
                            "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
                            "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
                            "outubro": 10, "novembro": 11, "dezembro": 12
                        }
                        month_num = months_map.get(month_part.lower())
                        
                    if month_num is None:
                        raise ValueError("Mês não reconhecido!")

                    now_dt = datetime.datetime.now()
                    
                    if now_dt.day <= 5:
                        adjusted_month = now_dt.month - 1
                        if adjusted_month == 0:
                            adjusted_month = 12
                            adjusted_year = now_dt.year - 1
                        else:
                            adjusted_year = now_dt.year
                    else:
                        adjusted_month = now_dt.month
                        adjusted_year = now_dt.year
                    
                    if month_num != adjusted_month or year_part != adjusted_year:
                        print(">> O email de compra não coincide com o mês esperado, pulando...")
                        return
                except Exception:
                    pass
                
                values["EMAILDATE"] = f"{month_num}/{year_part}"
                
                items = [
                    "Papel Higiênico Natureza 8X300mt", 
                    "Papel Toalha T19RS 06x200mt", 
                    "Papel Toalha T19RS 6X200mt",
                    "Sabonete Líquido Frescor da Manhã"
                ]
                
                centros = ["araguaia shopping", "terminal rodoviario"]
                
                for line in emailContent[emailContent.index("Nota Fiscal no valor total de"):].split('\n'):
                    stripLine = line.strip()
                                        
                    for centro in centros:
                        if centro in stripLine.lower().replace("ê", "e").replace("á", "a") and stripLine != "Estoque Disponível na R3 Suprimentos":
                            Actual_centro = stripLine
                            Value_found = False
                        elif stripLine == "Estoque Disponível na R3 Suprimentos":
                            Actual_centro = ""
                            Actual_item = ""
                            Value_found = False

                    if stripLine in items:
                        Actual_item = stripLine
                        Value_found = False

                    if Actual_centro != "" and Actual_item != "":
                        Temp_Value = float(stripLine.replace(",", ".")) if stripLine.isdigit() else 0

                        if Temp_Value > 0 and not Value_found:
                            if "araguaia shopping" in Actual_centro.lower():
                                if "papel higienico" in Actual_item.lower().replace("ê", "e"):
                                    values["COMLI"]["HIG"] = Temp_Value
                                    Value_found = True
                                elif "papel toalha" in Actual_item.lower().replace("á", "a"):
                                    values["COMLI"]["TOA"] = Temp_Value
                                    Value_found = True
                                elif "sabonete liquido" in Actual_item.lower().replace("í", "i"):
                                    values["COMLI"]["SAB"] = Temp_Value
                                    Value_found = True
                            elif "terminal rodoviario" in Actual_centro.lower().replace("á", "a"):
                                if "papel higienico" in Actual_item.lower().replace("ê", "e"):
                                    values["TR1"]["HIG"] = Temp_Value
                                    Value_found = True
                                elif "papel toalha" in Actual_item.lower().replace("á", "a"):
                                    values["TR1"]["TOA"] = Temp_Value
                                    Value_found = True
                                elif "sabonete liquido" in Actual_item.lower().replace("í", "i"):
                                    values["TR1"]["SAB"] = Temp_Value
                                    Value_found = True
                
                return values
            case _:
                raise Exception("Template not found!")