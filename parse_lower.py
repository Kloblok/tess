import os
import re
import pandas as pd

class ParserLower:
    def __init__(self):
        self.pattern = re.compile(r'ваш_шаблон_для_парсинга')  # Измените на нужный вам шаблон

    def run(self, directory_path):
        results = {}
        files = list(filter(lambda filename: filename.endswith("lower.txt"), os.listdir(directory_path)))
        df = pd.DataFrame(index=files)
        for filename in files:
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='UTF-8') as file:
                text = file.read()
            variants = list(filter(lambda variant: len(variant) != 0, text.split('Вариант')))
            for i, variant in enumerate(variants, start=1):
                results = self.parse_words(filename, variant, df, results, i)
        df.to_csv('results_lower.csv')
        df.sort_index(axis=1, ascending=True).to_excel('results_lower.xlsx')
        with open('results_lower.txt', 'w') as output_file:
            for word, value in results.items():
                output_file.write(f"{word}: {value}\n")

    def parse_words(self, filename, text, df, results, i):
        matches = self.pattern.findall(text)
        for name, value in matches:
            df.loc[filename, f'{name.lower()}-{i}'] = value
            results[name] = value
        return results
