
from typing import Type


class Knowledge():
    '''
    Базовый класс для представления всех экзаменационных билетов (для сайта PDD, так как там можно 3 раза ответить на вопрос и это будет 3 "очка")
    data[номер билета][номер вопроса]
    data[][] = value, если:
        value=-2, тогда пропускаем, независимо от того, что внутри
        value=-1, тогда не знаем, что внутри и поэтому будем сбрасывать до 0
        value=0 - тогда рассматриваем к редактированию
    '''
    def __init__(self):
        self.data = {}
        self._fill_const(-1)
        pass

    def get_zero_knowledge()->Type['Knowledge']:
        knowledge = Knowledge()
        knowledge._fill_const(-1)
        return knowledge
    
    def _fill_zero(self):
        return self._fill_const(0)
    def _fill_const(self,value=0):
        for i in range(0, 40):
            self.data[i] = {}
            for j in range(0, 20):
                self.data[i][j] = value
        return self

    def copy(knowledge:Type['Knowledge'])->Type['Knowledge']:
        result = Knowledge()
        for i in range(0, 40):
            result.data[i] = {}
            for j in range(0, 20):
                result.data[i][j] = knowledge.data[i][j]
        return knowledge

    def to_dict(self):
        #TODO добавить в наследуемый интефрейс
        return self.data
    def from_dict(dct:dict) -> Type['Knowledge']:
        #TODO добавить в наследуемый интефрейс
        result = Knowledge()
        for i in range(0, 40):
            result.data[i] = {}
            for j in range(0, 20):
                result.data[i][j] = dct[i][j]
        return result

def main():
    kn = Knowledge.get_zero_knowledge()
    print(kn.data)

if __name__=="__main__":
    main()