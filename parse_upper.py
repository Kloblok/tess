import os
import re
import pandas as pd

class Parser:

    directory_path = '/home/abramovarto/OCR/code/text_result1/'

    def __init__(self, directory_path):
        self.tpp_words = ['Урайнефтегаз', 'Покачёвнефтегаз', 'Повхнефтегаз', 'Лангепаснефтегаз', 'Когалымнефтегаз', 'Белоярскнефтегаз', 'Ямалнефтегаз']
        self.words_to_find = ['Куст:', 'Скважина', 'Месторождение', 'ЦДНГ', 'ЦИТС', 'УЭЦН:']
        self.pattern = '|'.join(re.escape(word) for word in self.words_to_find)
        self.pattern = rf'(?P<name>{"|".join([re.escape(word) for word in self.words_to_find])})\s+(?P<value>(?:\w|\d)+)'
        self.pattern_uecn = r'\b[\dА-Я]+(?:\.[\dА-Я]+)?(?:\S[\d\wА-Я]+)?-\s*\d{1,4}-\s*\d{4}\b'
        self.directory_path = directory_path

    def run(self, directory_path):
        results = {}
        files = list(filter(lambda filename: filename.endswith("upper.txt"), os.listdir(directory_path)))
        
        df = pd.DataFrame(index=files)
        for filename in files:
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='UTF-8') as file:
                text = file.read()
            variants = list(filter(lambda variant: len(variant) != 0, text.split('Вариант')))
            for i, variant in enumerate(variants, start=1):
                results = self.parse_words(pattern=self.pattern, filename=filename, text=variant, df=df, results=results, i=i)
        df.to_csv('results_upper.csv')
        df.sort_index(axis=1, ascending=True).to_excel('results_upper.xlsx')
        with open('results_upper.txt', 'w') as output_file:
            for word, value in results.items():
                output_file.write(f"{word}: {value}\n")

        df = pd.read_csv('results_upper.csv')
        column_filters = {
            'ТПП': self.check1,
            'УЭЦН': self.check2,
            'куст:': self.check3,
            'скважина': self.check4,
            'месторождение': self.check5,
            'цднг': self.check6,
            'цитс': self.check7,
        }

        result_df = pd.DataFrame(index=df.index, columns=['original_column'] + list(column_filters.keys()))
        for index in range(df.shape[0]):
            for column in column_filters.keys():
                for i in range(1, 6):
                    print(df.iloc[index][f'{column}-{i}'])
                    if column_filters[column](df.iloc[index][f'{column}-{i}']):
                        result_df.iloc[index][column] = df.iloc[index][f'{column}-{i}']
                        break
        result_df['original_column'] = df.iloc[:, 0]

        print(result_df)
        result_df.to_csv('result-fin.csv', index=True)
        result_df.to_excel('results-fin.xlsx')


    def check1(self, value):
        return value in self.tpp_words

    def check2(self, value):
        return re.search(self.pattern_uecn, str(value))

    def check3(self, value):
        return re.search(r'^(\d|d\w{1})+$', str(value))

    def check4(self, value):
        return re.search(r'(\d|\d\w{1})+', str(value))

    def check5(self, value):
        return re.search(r'^[А-Я]{1}[а-я]{5,}$', str(value))

    def check6(self, value):
        return re.search(r'^\d+$', str(value))

    def check7(self, value):
        return re.search(r'^[А-я]{1}[а-я]{3,}$', str(value))

    def parse_words(self, pattern, filename, text, df, results, i):
        matches = re.findall(pattern, text, re.IGNORECASE)

        for name, value in matches:
            df.loc[filename, f'{name.lower()}-{i}'] = value
            results[name] = value

        uecn_matches = re.findall(self.pattern_uecn, text)
        if uecn_matches:
            df.loc[filename, f'УЭЦН-{i}'] = uecn_matches
            results['УЭЦН'] = uecn_matches

        for tpp_word in self.tpp_words:
            if tpp_word.lower() in text.lower():
                df.loc[filename, f'ТПП-{i}'] = tpp_word
                results[tpp_word] = tpp_word
        return results
