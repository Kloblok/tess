import os
from preprocess import preprocess_pdf
from ocr_upper import perform_ocr_upper
from ocr_parse_lower import perform_ocr_lower, ParserLower
from parse_upper import ParserUpper

def main():
    pdf_directory = 'C:\\Users\\lozch\\OneDrive\\Рабочий стол\\prj\\ecn'
    image_result_directory = 'image_result'
    text_result_directory = 'text_result'

    # Создаем необходимые директории, если их нет
    os.makedirs(image_result_directory, exist_ok=True)
    os.makedirs(text_result_directory, exist_ok=True)

    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, filename)

            # Этап 1: Предобработка изображений
            print(f"Обработка файла: {pdf_path}")
            preprocess_pdf(pdf_path)
            print(f"Предобработка завершена для файла: {pdf_path}")

            # Этап 2: OCR для верхней части изображений
            print(f"OCR для верхней части: {pdf_path}")
            perform_ocr_upper(image_result_directory)
            print(f"OCR для верхней части завершен для файла: {pdf_path}")

            # Этап 3: OCR и парсинг для нижней части изображений
            print(f"OCR и парсинг для нижней части: {pdf_path}")
            perform_ocr_lower(image_result_directory)
            print(f"OCR и парсинг для нижней части завершен для файла: {pdf_path}")

            # Этап 4: Парсинг текста для верхней части изображений
            print(f"Парсинг текста для верхней части: {pdf_path}")
            upper_parser = ParserUpper()
            upper_parser.run(text_result_directory)
            print(f"Парсинг текста для верхней части завершен для файла: {pdf_path}")

            # Добавляем паузу между обработкой файлов, чтобы увидеть прогресс
            print(f"Обработка завершена для файла: {pdf_path}\n{'-'*40}\n")

if __name__ == "__main__":
    main()
