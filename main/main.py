import os
import sys
from pathlib import Path

from Rabota_s_png import extract_data_png
from Rabota_s_pdf import extract_data_pdf
from Rabota_s_docx import extract_data_docx


def extract_from_file(file_path: Path):
    """
    Определяет тип файла по расширению и вызывает соответствующий экстрактор.
    Возвращает кортеж (act_number, contract_number, date_value, total_amount)
    или None, если тип файла не поддерживается.
    """
    ext = file_path.suffix.lower()

    if ext == ".png":
        return extract_data_png(str(file_path))
    elif ext == ".pdf":
        return extract_data_pdf(str(file_path))
    elif ext == ".docx":
        # В docx порядок возврата: (doc_number, date, contract, amount)
        # Приводим к общему порядку: (act_number, contract_number, date, amount)
        doc_number, date_value, contract_number, total_amount = extract_data_docx(str(file_path))
        return doc_number, contract_number, date_value, total_amount
    else:
        return None


def scan_directory(directory: str, recursive: bool = False):
    """
    Обходит директорию и извлекает данные из всех поддерживаемых файлов.
    Возвращает список словарей с результатами.
    """
    supported_ext = {".png", ".pdf", ".docx"}
    results = []
    errors = []

    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"Ошибка: '{directory}' не является директорией")
        return [], []

    # Собираем файлы
    if recursive:
        files = [p for p in dir_path.rglob("*") if p.is_file() and p.suffix.lower() in supported_ext]
    else:
        files = [p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in supported_ext]

    if not files:
        print(f"В директории '{directory}' не найдено поддерживаемых файлов ({', '.join(supported_ext)})")
        return [], []

    print(f"Найдено файлов для обработки: {len(files)}\n")

    for file_path in sorted(files):
        print("=" * 60)
        print(f"Файл: {file_path.name}")
        print("=" * 60)

        try:
            data = extract_from_file(file_path)
        except Exception as e:
            print(f"  [!] Ошибка при обработке: {e}\n")
            errors.append({"file": str(file_path), "error": str(e)})
            continue

        if data is None:
            print(f"  [!] Неподдерживаемый тип файла, пропуск\n")
            continue

        act_number, contract_number, date_value, total_amount = data
        results.append({
            "file": str(file_path),
            "act_number": act_number,
            "contract_number": contract_number,
            "date": date_value,
            "amount": total_amount,
        })

        print(f"  Номер документа: {act_number}")
        print(f"  Номер договора:  {contract_number}")
        print(f"  Дата:            {date_value}")
        print(f"  Итоговая сумма:  {total_amount} руб.\n")

    return results, errors


def print_summary(results, errors):
    """Печатает итоговую сводку по всем обработанным файлам."""
    print("\n" + "=" * 60)
    print("ИТОГОВАЯ СВОДКА")
    print("=" * 60)

    if not results:
        print("Нет успешно обработанных файлов.")
    else:
        # Заголовок таблицы
        header = f"{'Файл':<40} | {'Акт':<12} | {'Договор':<14} | {'Дата':<12} | {'Сумма':>12}"
        print(header)
        print("-" * len(header))

        for row in results:
            file_name = Path(row["file"]).name
            if len(file_name) > 38:
                file_name = file_name[:35] + "..."
            act = row["act_number"] or "-"
            contract = row["contract_number"] or "-"
            date = row["date"] or "-"
            amount = f"{row['amount']:.2f}" if row["amount"] is not None else "-"
            print(f"{file_name:<40} | {act:<12} | {contract:<14} | {date:<12} | {amount:>12}")

    if errors:
        print(f"\nОшибок при обработке: {len(errors)}")
        for err in errors:
            print(f"  - {Path(err['file']).name}: {err['error']}")


def main():
    # Директория по умолчанию — текущая, либо первый аргумент командной строки
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."

    # Флаг --recursive для обхода подпапок
    recursive = "--recursive" in sys.argv or "-r" in sys.argv

    print(f"Сканирование директории: {os.path.abspath(directory)}")
    if recursive:
        print("Режим: рекурсивный обход")
    print()

    results, errors = scan_directory(directory, recursive=recursive)
    print_summary(results, errors)

    # Возвращаем ненулевой код, если были ошибки — удобно для скриптов/CI
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
