
from typing import Type


class Knowledge():
    '''
    data[номер билета][номер вопроса]
    data[][] = value, если:
        value=-2, тогда пропускаем, независимо от того, что внутри
        value=-1, тогда не знаем, что внутри и поэтому будем сбрасывать до 0
        value=0 - тогда рассматриваем к редактированию
    '''
    def __init__(self):
        self.data = {}
        self._fill_zero()
        pass

    def get_zero_knowledge()->Type['Knowledge']:
        knowledge = Knowledge()
        knowledge._fill_zero()
        return knowledge
    
    def _fill_zero(self):
        for i in range(0, 40):
            self.data[i] = {}
            for j in range(0, 20):
                self.data[i][j] = 0
        return self.data

    def copy(knowledge:Type['Knowledge'])->Type['Knowledge']:
        result = Knowledge()
        for i in range(0, 40):
            result.data[i] = {}
            for j in range(0, 20):
                result.data[i][j] = knowledge[i][j]
        return knowledge

def main():
    kn = Knowledge.get_zero_knowledge()
    print(kn.data)

if __name__=="__main__":
    main()