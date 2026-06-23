import os
import sys
import time
import modules
import pyfiglet
import datetime
import tempfile
import traceback
import subprocess

from datetime import date
from dotenv import load_dotenv


print("Inicializando, aguarde...")

load_dotenv()

type_dict = {
    "BOX": "Caixas",
    "ROL": "Rolos",
    "GAL": "Galões"
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def figlet(message: str) -> None:
    clear()
    print(pyfiglet.figlet_format(
        message, font="roman", width=170, justify="center"))

def CMDAuxiliar(mensagem: list[str] | str, preFilledCommand: str = "") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        temp_path = tmp.name

    summary_text = "\n".join(mensagem) if isinstance(mensagem, list) else mensagem
    python_script = "import sys; summary = sys.argv[1]; preFilledCommand = sys.argv[2]; path = sys.argv[3]; print(summary); result = input(f'Comando {preFilledCommand} > '); open(path, 'w', encoding='utf-8').write(result)"
    subprocess.run(
        ['python', '-c', python_script, summary_text, f"({preFilledCommand})", temp_path],
        text=True, encoding='cp850',
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    with open(temp_path, encoding='utf-8') as f:
        user_input = f.read().strip().lower()
    os.remove(temp_path)

    return user_input

def printPreview(stock):
    confirmMessage = ""

    def calc_stock_needed(needed: float, min_value: float, available: float) -> float:
        if needed < min_value:
            return 0
        return min(needed, available)

    StockNeeded_hig = calc_stock_needed(
        stock["IDEAL"]["HIG"] - stock["ALMOX"]["HIG"],
        min_value=stock["MINIMUM"]["HIG"],
        available=stock["R3"]["HIG"]
    )

    StockNeeded_toa = calc_stock_needed(
        stock["IDEAL"]["TOA"] - stock["ALMOX"]["TOA"],
        min_value=stock["MINIMUM"]["TOA"],
        available=stock["R3"]["TOA"]
    )

    StockNeeded_sab = calc_stock_needed(
        stock["IDEAL"]["SAB"] - stock["ALMOX"]["SAB"],
        min_value=stock["MINIMUM"]["SAB"],
        available=stock["R3"]["SAB"]
    )

    summary_lines = [
        "\n> Resumo:\n",
        "\nNos temos:\n",
        f"{stock["ALMOX"]["HIG"]} {stock["ALMOX"]["HIG"]["UNITYTYPE"]}",
        f"{stock["ALMOX"]["TOA"]} {stock["ALMOX"]["TOA"]["UNITYTYPE"]}",
        f"{stock["ALMOX"]["SAB"]} {stock["ALMOX"]["SAB"]["UNITYTYPE"]}\n",
        "\nNa requinte temos:\n",
        f"{stock["R3"]["HIG"]} {stock["R3"]["HIG"]["UNITYTYPE"]}",
        f"{stock["R3"]["TOA"]} {stock["R3"]["TOA"]["UNITYTYPE"]}",
        f"{stock["R3"]["SAB"]} {stock["R3"]["SAB"]["UNITYTYPE"]}\n",
    ]
    
    if StockNeeded_hig >= 0 or StockNeeded_toa >= 0 or StockNeeded_sab >= 0:
        summary_lines.append(f"\n> Precisamos pedir:\n")
        summary_lines.append("{:.2f} ".format(StockNeeded_hig) + stock["ALMOX"]["HIG"]["UNITYTYPE"])
        summary_lines.append("{:.2f} ".format(StockNeeded_toa) + stock["ALMOX"]["TOA"]["UNITYTYPE"])
        summary_lines.append("{:.2f} ".format(StockNeeded_sab) + stock["ALMOX"]["SAB"]["UNITYTYPE"])

        confirmMessage = "\\n[1] - Confirmar \\n[2] - Alterar valores do pedido\\n[0] - Cancelar\\n "
    else:
        summary_lines.append("\n>> Não precisamos pedir nada ainda.")
        confirmMessage = "\\n[1] - confirmar \\n[2] - adicionar valor extra no pedido\\n[0] - Cancelar\\n"

    user_input = CMDAuxiliar(confirmMessage, "1")
    
    if user_input == "1" or user_input == "":
        return True, {
            "HIG": "{:.2f}".format(StockNeeded_hig), 
            "TOA": "{:.2f}".format(StockNeeded_toa), 
            "SAB": "{:.2f}".format(StockNeeded_sab)
        }
    elif user_input == "2":
        complete = False

        while not complete:
            summary_lines = [
                "\nEstoque Atual:\n",
                f"PAPEL HIGIGÊNICO: {stock['ALMOX']["HIG"]["QUANTITY"]} {stock["ALMOX"]["HIG"]["UNITYTYPE"]}",
                f"PAPEL TOALHA: {stock['ALMOX']["TOA"]["QUANTITY"]} {stock["ALMOX"]["TOA"]["UNITYTYPE"]}",
                f"SABONETE LIQUIDO: {stock['ALMOX']["SAB"]["QUANTITY"]} {stock["ALMOX"]["SAB"]["UNITYTYPE"]}\n",
                "\nEstoque R3:\n",
                f"PAPEL HIGIGÊNICO: {stock['R3']["HIG"]["QUANTITY"]} {stock["ALMOX"]["HIG"]["UNITYTYPE"]}",
                f"PAPEL TOALHA: {stock['R3']["TOA"]["QUANTITY"]} {stock["ALMOX"]["TOA"]["UNITYTYPE"]}",
                f"SABONETE LIQUIDO: {stock['R3']["SAB"]["QUANTITY"]} {stock["ALMOX"]["SAB"]["UNITYTYPE"]}\n",
                "\n> Valores a solicitar:\n",
                f"[1] - PAPEL HIGIGÊNICO: {StockNeeded_hig} {stock["ALMOX"]["HIG"]["UNITYTYPE"]}",
                f"[2] - PAPEL TOALHA: {StockNeeded_toa} {stock["ALMOX"]["TOA"]["UNITYTYPE"]}",
                f"[3] - SABONETE LIQUIDO: {StockNeeded_sab} {stock["ALMOX"]["SAB"]["UNITYTYPE"]}\n",
                "[9] - Cancelar\n",
                "[0] - Confirmar\n",
                "\nDigite o numero do produto a ser alterado"
            ]

            opc = CMDAuxiliar(summary_lines, "0")

            if opc == "0" or opc == "":
                return True, {
                    "HIG": StockNeeded_hig, 
                    "TOA": StockNeeded_toa, 
                    "SAB": StockNeeded_sab
                }

            if opc == "9":
                return False, {}

            if opc not in ("1", "2", "3"):
                CMDAuxiliar("\n>>> Opção inválida. Pressione ENTER para continuar.")
                continue

            valor_str = CMDAuxiliar("\n> Digite o valor a somar/subtrair (ex: 5 ou -3)")

            try:
                valor = float(valor_str)
            except:
                CMDAuxiliar("\n>>> Valor inválido. Pressione ENTER para continuar.")
                continue

            if opc == "1":
                if valor > stock['R3']["HIG"]:
                    StockNeeded_hig = stock['R3']["HIG"]
                else:
                    StockNeeded_hig += valor
            elif opc == "2":
                if valor > stock['R3']["TOA"]:
                    StockNeeded_toa = stock['R3']["TOA"]
                else:
                    StockNeeded_toa += valor
            elif opc == "3":
                if valor > stock['R3']["SAB"]:
                    StockNeeded_sab = stock['R3']["SAB"]
                else:
                    StockNeeded_sab += valor
    return False, {}

def close(sql, webmail, pdf):
    print("\n> Terminando programa...")
    sql.connector.close()
    webmail.driver.quit()
    # pdf.flush()
    
def Main():
    on = True

    WebmailFullScreen = True

    args = sys.argv[1] if len(sys.argv) > 1 else None
    
    while on:
        clear()

        figlet("ALMOXARIFADO")

        print(
            "Bem vindo ao sistema de higiênicos do almoxarifado!\n" +
            "Escolha uma das opções abaixo:\n"
        )

        script_choise = input(
            "[1] - Pedido de higiênico semanal\n" +
            "[2] - Relatório de higiênicos mensal\n" +
            "[0] - Sair\n\n" +
            "Comando (0) >"
        ) if not args else args

        if script_choise == "0" or script_choise == "":
            on = False
            figlet("Ate mais <3")
            time.sleep(2)
            quit()
            return

        clear()
        if script_choise == "1":
            EMAIL_BUYER = os.getenv("EMAIL_BUYER")
            EMAIL_HYGIENIC_SUPPLIER = os.getenv("EMAIL_HYGIENIC_SUPPLIER")
            EMAIL_SHOPPING_SUPERVISOR = os.getenv("EMAIL_SHOPPING_SUPERVISOR")
            EMAIL_OPERATIONAL_SUPERVISOR = os.getenv("EMAIL_OPERATIONAL_SUPERVISOR")
            
            figlet("PEDIDOS")

            if not EMAIL_BUYER or not EMAIL_HYGIENIC_SUPPLIER or not EMAIL_SHOPPING_SUPERVISOR or not EMAIL_OPERATIONAL_SUPERVISOR:
                raise Exception("Environement not set!")

            webmail = modules.WebmailCore(30, WebmailFullScreen)
            sql = modules.DBCore()

            stock = {
                "R3": {
                    "HIG": {
                        "QUANTITY": 0.0,
                        "UNITYTYPE": ""
                    },
                    "TOA": {
                        "QUANTITY": 0.0,
                        "UNITYTYPE": ""
                    },
                    "SAB": {
                        "QUANTITY": 0.0,
                        "UNITYTYPE": ""
                    }
                },
                
                "ALMOX": {
                    "HIG": {
                        "QUANTITY": 0.0,
                        "UNITYTYPE": ""
                    },
                    "TOA": {
                        "QUANTITY": 0.0,
                        "UNITYTYPE": ""
                    },
                    "SAB": {
                        "QUANTITY": 0.0,
                        "UNITYTYPE": ""
                    }
                },

                "MINIMUM": {
                    "HIG": 0.0,
                    "TOA": 0.0,
                    "SAB": 0.0
                },

                "IDEAL": {
                    "HIG": 0.0,
                    "TOA": 0.0,
                    "SAB": 0.0
                }
            }

            for item in sql.selectStock():
                place = item["place"]

                if item["id"] == 1322:
                    key = "HIG"
                elif item["id"] == 1323:
                    key = "TOA"
                elif item["id"] == 1324:
                    key = "SAB"
                else:
                    continue

                stock[place][key]["QUANTITY"] = item["quantity"]
                
                stock[place][key]["UNITYTYPE"] = item["unityType"]

                if item["minimum"] is not None:
                    stock["MINIMUM"][key] = item["minimum"]

                if item["ideal"] is not None:
                    stock["IDEAL"][key] = item["ideal"]

            # place = "receive" or "sent"
            emailContent = webmail.fetchEmail(f"{EMAIL_BUYER} Pedido de Compra Terminal Rodoviário de Goiânia e Araguaia Shopping", "receive")

            if extractedValues := webmail.extractValues(emailContent, "EDIELSON"):
                totalPurchaseHig = extractedValues["COMLI"]["HIG"] + \
                    extractedValues["TR1"]["HIG"]
                totalPurchaseToa = extractedValues["COMLI"]["TOA"] + \
                    extractedValues["TR1"]["TOA"]
                totalPurchaseSab = extractedValues["COMLI"]["SAB"] + \
                    extractedValues["TR1"]["SAB"]

                if sql.inserPurchase("R3", totalPurchaseHig, totalPurchaseToa, totalPurchaseSab, date=extractedValues["EMAILDATE"]):
                    stock['R3']['HIG'] += totalPurchaseHig
                    stock['R3']['TOA'] += totalPurchaseToa
                    stock['R3']['SAB'] += totalPurchaseSab
                else:
                    print(">> Compra já adicionada ao sistema! Pulando...")

            purchaseNeeded, valuesNeeded = printPreview(stock)

            if purchaseNeeded:
                webmail.sendEmail(
                    "shipment", 
                    [EMAIL_HYGIENIC_SUPPLIER],
                    [EMAIL_OPERATIONAL_SUPERVISOR, EMAIL_BUYER, EMAIL_SHOPPING_SUPERVISOR],
                    actualStock=stock,
                    stockNeeded=valuesNeeded
                )

                sql.inserPurchase("ALMOX", valuesNeeded["HIG"], valuesNeeded["TOA"], valuesNeeded["SAB"], 0)

            close(sql, webmail, pdf)
        elif script_choise == "2":
            clear()
            
            figlet("RELATORIO")
            
            EMAIL_BUYER = os.getenv("EMAIL_BUYER")
            EMAIL_TR_SUPERVISOR = os.getenv("EMAIL_TR_SUPERVISOR")
            EMAIL_SHOPPING_SUPERVISOR = os.getenv("EMAIL_SHOPPING_SUPERVISOR")
            EMAIL_OPERATIONAL_SUPERVISOR = os.getenv("EMAIL_OPERATIONAL_SUPERVISOR")
            
            if not EMAIL_BUYER or not EMAIL_TR_SUPERVISOR or not EMAIL_SHOPPING_SUPERVISOR or not EMAIL_OPERATIONAL_SUPERVISOR:
                raise Exception("Environement not set!")
            
            webmail = modules.WebmailCore(30, WebmailFullScreen)
            sql = modules.DBCore()
            pdf = modules.PDFManipulator()
            
            today = date.today().replace(day=1)
            
            start_date: date
            
            if today.day > 6:
                start_date = today - datetime.timedelta(days=1)
            else:
                start_date = today
            
            finish_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            
            movement_type = "Saída de Materiais"
            
            reportValues = {}
            
            for CC in ["COMLI", "TR1", "TOTAL"]:
                movements = sql.selectMovement(start_date.strftime("%Y-%m-%d"), finish_date.strftime("%Y-%m-%d"), CC, fetchOne=False)
                
                if movements == None:
                    print(">> Nenhum movimento foi detectado, encerrando relatorio...")
                    close(sql, webmail, pdf)
                    return
                
                reportValues[CC] = pdf.generate(movements, start_date.strftime("%d/%m/%Y"), finish_date.strftime("%d/%m/%Y"), movement_type, CC)

            stockTotal = {
                "hig": 0.0,
                "toa": 0.0,
                "sab": 0.0
            }

            for item in sql.selectStock():
                if item["id"] in [1322, 1212]:
                    stockTotal['hig'] += item["quantity"]
                elif item["id"] in [1323, 1213]:
                    stockTotal['toa'] += item["quantity"] if item["place"] == "R3" else item["quantity"] / 6
                elif item["id"] in [1324, 1214]:
                    stockTotal['sab'] += item["quantity"]

            # place = "receive" or "sent"
            emailContent = webmail.fetchEmail(f"{EMAIL_BUYER} Pedido de Compra Terminal Rodoviário de Goiânia e Araguaia Shopping", "receive")

            if extractedValues := webmail.extractValues(emailContent, "EDIELSON"):
                totalPurchaseHig = extractedValues["COMLI"]["HIG"] + \
                    extractedValues["TR1"]["HIG"]
                totalPurchaseToa = extractedValues["COMLI"]["TOA"] + \
                    extractedValues["TR1"]["TOA"]
                totalPurchaseSab = extractedValues["COMLI"]["SAB"] + \
                    extractedValues["TR1"]["SAB"]

                if sql.inserPurchase("R3", totalPurchaseHig, totalPurchaseToa, totalPurchaseSab, date=extractedValues["EMAILDATE"]):
                    stockTotal['hig'] += totalPurchaseHig
                    stockTotal['toa'] += totalPurchaseToa
                    stockTotal['sab'] += totalPurchaseSab
                else:
                    print(">> Compra já adicionada ao sistema! Pulando...")
                    
            webmail.sendEmail(
                "report", 
                # ["guga.4004@hotmail.com"],
                [EMAIL_SHOPPING_SUPERVISOR],
                [EMAIL_OPERATIONAL_SUPERVISOR, EMAIL_BUYER, EMAIL_TR_SUPERVISOR],
                startDate=start_date,
                finishDate=finish_date,
                reportValues=reportValues,
                stockTotal=stockTotal
            )
        
            close(sql, webmail, pdf)
        args = None

if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        input(f">>> Fatal Error --> {e}\n{traceback.format_exc()}")
