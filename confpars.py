import re
class ParsBase:
    def __init__(self, data):
        self.data = data

    def pars(self):
        raise NotImplementedError


class pars1(ParsBase):
    def validate(self):
        #! ААА
        pattern = re.compile(r'^(?![А-Я]{3}$)')
        return bool(pattern.search(self.data))

class pars2(ParsBase):
    def validate(self):
        # ---
        pattern1 = re.compile(r'--{2,}')
        pattern2 = re.compile(r'- - +')
        #pattern3 = re.compile(r'\b[а-я][а-яА-Я]*\b')
        pattern4 = re.compile(r'^[А-Я]{2}$'or r'^[А-Я][а-я]{2}$')
        pattern5 = re.compile(r'^[а-я]{3}$')
        return bool(pattern1.search(self.data) or pattern2.search(self.data) or pattern4.search(self.data) or pattern5.search(self.data)) 


class pars3(ParsBase):
    def validate(self):
        # АА
        pattern = re.compile(r'^[А-Я]{2}$'or r'^[А-Я][а-я]{2}$')
        return bool(pattern.search(self.data))

class pars4(ParsBase):
    def validate(self):
        # словарь
        pattern = re.compile(r'\b((?-i:Насос)|(?-i:Кабель-удлинитель)|(?-i:Обратные клапана)|(?-i:КС/Шламоуловитель)|(ПЭД)|(?-i:Протекор)|(?-i:Компенсатор)|(?-i:Газосепаратор)|(?-i:Вход. модуль)|(?-i:Кабель/№ каб.барабана)|(ТМС)|(?-i:Вставка имп.кабеля))\b')
        return bool(pattern.search(self.data))
