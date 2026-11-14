import re
import pytesseract
from PIL import Image
# работа с png

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_png(png_path):
    img = Image.open(png_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    text = pytesseract.image_to_string(img, lang="rus+eng")
    return text

def extract_data_png(png_path):
    full_text = extract_text_from_png(png_path)
    print("Текст документа:")
    print(full_text)
    print("-" * 40)

    # Ищем номер акта
    act_number = None
    act_match = re.search(r"№\s*([^\s]+)", full_text)
    if act_match:
        act_number = act_match.group(1).strip()
    else:
        first_line = full_text.split("\n", 1)[0]
        words = first_line.split()
        if len(words) >= 1:
            act_number = words[-1]

    # Ищем номер договора
    contract_number = None
    contract_match = re.search(r"Договор\s*:?\s+([0-9][0-9/\-]*)", full_text)
    if contract_match:
        contract_number = contract_match.group(1).strip()
    else:
        basis_match = re.search(r"Основание\s*:?\s+([0-9][0-9/\-]*)", full_text)
        if basis_match:
            contract_number = basis_match.group(1).strip()
        else:
            fallback_match = re.search(r"\b(\d{2}/\d{2}/\d{2}-\d{2})\b", full_text)
            if fallback_match:
                contract_number = fallback_match.group(1)

    # Ищем дату
    date_value = None
    date_match = re.search(r"Дата(?:\s+документа)?\s*:?\s+(\d{2}\.\d{2}\.\d{4})", full_text)
    if date_match:
        date_value = date_match.group(1).strip()
    else:
        date_fallback = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", full_text)
        if date_fallback:
            date_value = date_fallback.group(1)

    # Ищем итоговую сумму
    sum_match = re.search(r"\s*([\d\s]+,\d{2})\s*руб", full_text)
    if sum_match:
        sum_raw = sum_match.group(1).replace(" ", "").replace(",", ".")
        total_amount = float(sum_raw)
    else:
        total_amount = None

    return act_number, contract_number, date_value, total_amount


# Пример
if __name__ == "__main__":
    act, contract, date, amount = extract_data_png("12_Акт_связь_0426.png")
    print("Номер документа (акта, УПД):", act)
    print("Номер договора:", contract)
    print("Дата:", date)
    print("Итоговая сумма:", amount, "руб.")
