import re
import pymupdf
import pytesseract
from PIL import Image
# работа с pdf

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def fix_mojibake(text):
    try:
        fixed = text.encode("latin-1", errors="ignore").decode("cp1251", errors="ignore")
        if len(re.findall(r"[А-Яа-яЁё]", fixed)) > len(re.findall(r"[А-Яа-яЁё]", text)):
            return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return text

def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    full_text = fix_mojibake(full_text)
    cyrillic_count = len(re.findall(r"[А-Яа-яЁё]", full_text))

    if not full_text.strip() or cyrillic_count < 10:
        print("Текстовый слой нечитаем или отсутствует")
        doc = pymupdf.open(pdf_path)
        full_text = ""
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img, lang="rus+eng")
            full_text += page_text + "\n"
        doc.close()
    return full_text

def extract_data_pdf(pdf_path):
    full_text = extract_text_from_pdf(pdf_path)
    print("Текст документа:")
    print(full_text)

    # Ищем номер акта
    act_number = None
    act_match = re.search(r"№\s*([^\s]+)", full_text)
    if act_match:
        act_number = act_match.group(1).strip()
    else:
        first_line = full_text.split("\n", 1)[0]
        words = first_line.split()
        if len(words) >= 1:
            act_number = words[-1] # добавить исключение, если не найден номер акта

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
                contract_number = fallback_match.group(1) # добавить исключение, если не найден номер договора

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
        total_amount = None # добавить исключение, если не найдена итоговая сумма

    return act_number, contract_number, date_value, total_amount

# 4, 8 и 15 сканы

# Пример
if __name__ == "__main__":
    act, contract, date, amount = extract_data_pdf("04_Акт_118_28-01-2026.pdf") # добавить проверку на копии
    print("Номер документа (акта, УПД):", act)
    print("Номер договора:", contract)
    print("Дата:", date)
    print("Итоговая сумма:", amount, "руб.")
