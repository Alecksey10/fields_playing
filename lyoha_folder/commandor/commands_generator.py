from enum import Enum
import random
from typing import Optional
import sys
sys.path.append('.')
from commandor.knowledge.knowledge import Knowledge
from commands.bilet_commands.answer_question import AnswerQuestion
from commands.bilet_commands.choose_bilet import ChooseBilet
from commands.bilet_commands.choose_question import ChooseQuestion
from commands.command_base import CommandBase
from commands.bilet_commands.end_bilet import EndBilet
from commands.bilet_commands.start_bilet import StartBilet

class CommandsGeneratorStates(Enum):
    START=0
    CHOOSING_BILET=1
    CHOOSING_QUESTION=2
    ANSWER_QUESTION=3
    CHECK_CURRENT_BILET=4
    STOP=5



class CommandsGenerator():
    def __init__(self, target_knowledge:Knowledge, start_knowledge=None):
        self.target_knowledge = target_knowledge
        self.current_knowledge:Knowledge = None
        if(start_knowledge):
            self.current_knowledge = Knowledge.copy(start_knowledge)
        else:
            self.current_knowledge = Knowledge.get_zero_knowledge()
        self.current_bilet = -1
        self.current_question = -1
        self.current_state = CommandsGeneratorStates.START
        self.current_delta = 0
        
    def __iter__(self):
        return self
    
    def __next__(self) -> CommandBase:

        while True:
            self.current_delta=0
            '''По циклу до выбора нужного состояния'''
            if(self.current_state == CommandsGeneratorStates.START):
                self.current_bilet = -1
                self.current_question = -1
                unmatched_bilet = self.find_unmatched_bilet()
                self.current_bilet = unmatched_bilet
                if(unmatched_bilet!=None):
                    self.current_state = CommandsGeneratorStates.CHOOSING_BILET
                    return ChooseBilet(unmatched_bilet)
                else:
                    self.current_state = CommandsGeneratorStates.STOP
                    raise StopIteration
            if(self.current_state==CommandsGeneratorStates.CHOOSING_BILET):
                unmatched_question = self.find_unmatched_question(self.current_bilet, question_after_id=self.current_question)
                if(unmatched_question!=None):
                    self.current_question = unmatched_question

                if(unmatched_question!=None):
                    self.current_state = CommandsGeneratorStates.CHOOSING_QUESTION
                    return ChooseQuestion(unmatched_question)
                else:
                    raise Exception("something has gone wrong, unmatched bilet, but all questions are matching")
            
            if(self.current_state==CommandsGeneratorStates.CHECK_CURRENT_BILET):
                '''Если не на что отвечать, скипаем'''
                unmatched_bilet = self.find_unmatched_bilet()
                if(unmatched_bilet!=None):
                    if(unmatched_bilet==self.current_bilet):
                        '''Если тот же билет, то пропускаем текущий вопрос, чтобы не перезагружать билет, потом на него ответим в конце'''
                        unmatched_question_after = self.find_unmatched_question(unmatched_bilet, question_after_id=self.current_question)
                        if(unmatched_question_after):
                            self.current_state = CommandsGeneratorStates.CHOOSING_BILET
                            continue
                        else:
                            self.current_state = CommandsGeneratorStates.START
                            continue

                    else:
                        self.current_state = CommandsGeneratorStates.START
                        continue
                else:
                    self.current_state = CommandsGeneratorStates.STOP
                    raise StopIteration

            if(self.current_state==CommandsGeneratorStates.CHOOSING_QUESTION):
                if(self.current_knowledge.data[self.current_bilet][self.current_question]==-1):
                    self.current_state = CommandsGeneratorStates.CHECK_CURRENT_BILET
                    self.current_delta=-1
                    return AnswerQuestion(False)
                elif(self.target_knowledge.data[self.current_bilet][self.current_question]<
                    self.current_knowledge.data[self.current_bilet][self.current_question]):
                    self.current_state = CommandsGeneratorStates.CHECK_CURRENT_BILET
                    self.current_delta=-1
                    return AnswerQuestion(False)
                else:
                    self.current_state = CommandsGeneratorStates.CHECK_CURRENT_BILET
                    self.current_delta=1
                    return AnswerQuestion(True)
            

    def update_current_knowledge(self, knowledge:Knowledge):
        '''При любом изменении билета или прочих данных надо обновлять knowledge'''
        self.current_knowledge = knowledge.copy()        
    
    def find_unmatched_bilet(self) -> Optional[int]:
        for i in range(0, 40):
            for j in range(0, 20):
                if(self.current_knowledge.data[i][j]==-2):
                    continue
                elif(self.current_knowledge.data[i][j]!=self.target_knowledge.data[i][j]):
                    return i
        return None

    def find_unmatched_question(self, bilet_id:int, question_after_id=-1) -> Optional[int]:
        for j in range(0, 20):
            if(self.current_knowledge.data[bilet_id][j]==-2):
                continue
            elif(self.current_knowledge.data[bilet_id][j]!=self.target_knowledge.data[bilet_id][j]
                 and j>question_after_id):
                return j
        return None
    
    def shift_last_question(self):
        '''Применяем подразумеваемые изменения к последнему выбранному билету'''
        
        if(self.current_state == CommandsGeneratorStates.CHECK_CURRENT_BILET):
            if(self.current_delta==-1):
                self.current_knowledge.data[self.current_bilet][self.current_question] = 0
                print(self.current_question)
            elif(self.current_delta==1):
                self.current_knowledge.data[self.current_bilet][self.current_question] += 1
                print(self.current_question)

def main():
    
    knowledge = Knowledge()
    for i in range(0, 20):
        knowledge.data[0][i] = random.randint(0, 3 )
    gen = CommandsGenerator(knowledge)
    while True:
        gen.shift_last_question()
        print(next(gen).to_dict())
        

if __name__=="__main__":
    main()