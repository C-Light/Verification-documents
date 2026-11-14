import re
from docx import Document
# работа с docx

MONTHS = {
    "январь": "01", "февраль": "02", "март": "03", "апрель": "04",
    "май": "05", "июнь": "06", "июль": "07", "август": "08",
    "сентябрь": "09", "октябрь": "10", "ноябрь": "11", "декабрь": "12",
}

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    parts = []

    for paragraph in doc.paragraphs:
        parts.append(paragraph.text)

    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells]
            parts.append(" | ".join(row_cells))

    return "\n".join(parts)


def extract_data_docx(docx_path):
    full_text = extract_text_from_docx(docx_path)
    print("Текст документа:")
    print(full_text)

    # Ищем номер документа
    doc_number = None
    number_match = re.search(
        r"Справка[^\n]*?\s([A-ZА-Я]{2,}\s?\d{2}-\d{2})",
        full_text
    )
    if number_match:
        doc_number = number_match.group(1).strip()
    else:
        number_match = re.search(r"№\s*([^\s]+)", full_text)
        if number_match:
            doc_number = number_match.group(1).strip()
        else:
            # Вариант 3: последнее слово первой строки
            first_line = full_text.split("\n", 1)[0]
            words = first_line.split()
        if len(words) >= 1:
            doc_number = words[-1]

    # Ищем дату
    date_value = None
    date_match = re.search(r"Дата(?:\s+документа)?\s*:?\s*(\d{2}\.\d{2}\.\d{4})", full_text)
    if date_match:
        date_value = date_match.group(1).strip()
    else:
        period_match = re.search(
            r"Период\s*:?\s*([А-Яа-яЁё]+)\s+(\d{4})",
            full_text
        )
        if period_match:
            month_name = period_match.group(1).lower()
            year = period_match.group(2)
            month_num = MONTHS.get(month_name)
            if month_num:
                date_value = f"{month_num}.{year}"
        else:
            date_fallback = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", full_text)
            if date_fallback:
                date_value = date_fallback.group(1)

    # Ищем номер договора
    contract_number = None
    contract_match = re.search(r"Договор\s*:?\s*([0-9][0-9/\-]*)", full_text)
    if contract_match:
        contract_number = contract_match.group(1).strip()
    else:
        basis_match = re.search(r"Основание\s*:?\s*([0-9][0-9/\-]*)", full_text)
        if basis_match:
            contract_number = basis_match.group(1).strip()
        else:
            # Запасной вариант: номер формата 24/03/15-01 где угодно
            fallback = re.search(r"\b(\d{2}/\d{2}/\d{2}-\d{2})\b", full_text)
            if fallback:
                contract_number = fallback.group(1)

    # Ищем итоговую сумму
    # Ищем число с разделителями тысяч и двумя знаками после запятой
    total_amount = None
    sum_match = re.search(r"([\d\s\u00A0]+,\d{2})", full_text)
    if sum_match:
        sum_raw = (
            sum_match.group(1)
            .replace(" ", "")
            .replace("\u00A0", "")  # неразрывный пробел
            .replace(",", ".")
        )
        total_amount = float(sum_raw)

    return doc_number, date_value, contract_number, total_amount


if __name__ == "__main__":
    number, date, contract, amount = extract_data_docx("11_Справка_ИТ_03-26.docx")
    print("Номер документа:", number)
    print("Номер договора:", contract)
    print("Дата:", date)
    print("Итоговая сумма:", amount, "руб.")
