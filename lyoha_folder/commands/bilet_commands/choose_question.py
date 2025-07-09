from commands.command_base import CommandBase


class ChooseQuestion(CommandBase):
    command_id = 3
    def __init__(self, question_number:int):
        self.question_number = question_number
        super().__init__()
    
    def to_dict(self):
        return {"question_number":self.question_number}
        
    @classmethod
    def from_dict(self, dct):
        return ChooseQuestion(question_number=dct.get('question_number'))