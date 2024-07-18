import os
#from preprocess_and_ocr_upper import process_pdf
from parse_upper import Parser
from ocr_parse_lower import ParserLower

def main():
    pdf_directory = '/home/abramovarto/OCR/pdf_files'
    image_result_directory = '/home/abramovarto/OCR/image_result'
    text_result_directory = '/home/abramovarto/OCR/code/text_result1'
    os.makedirs(image_result_directory, exist_ok=True)
    os.makedirs(text_result_directory, exist_ok=True)

    # Этап 2: Парсинг текста для верхней части изображений
    upper_parser = Parser(text_result_directory)
    upper_parser.run(text_result_directory)
    print(f"Парсинг текста для верхней части завершен для файла: {pdf_path}")




    for filename in os.listdir(pdf_directory):
        if filename.endswith('.PDF'):
            pdf_path = os.path.join(pdf_directory, filename)
            print(123) 


            # Этап 2: Парсинг текста для верхней части изображений
            print(f"Парсинг текста для верхней части: {pdf_path}")
            upper_parser = Parser(image_result_directory)
            upper_parser.run()
            print(f"Парсинг текста для верхней части завершен для файла: {pdf_path}")

            # Этап 3: OCR и парсинг для нижней части изображений
            print(f"OCR и парсинг для нижней части: {pdf_path}")
            process_table_image()
            perform_ocr_lower(text_result_directory, process_table_image, ocr_table_image)
            lower_parser = ParserLower(pdf_path)
            lower_parser.run(text_result_directory)
            print(f"OCR и парсинг для нижней части завершен для файла: {pdf_path}")

if __name__ == "__main__":
    main()
