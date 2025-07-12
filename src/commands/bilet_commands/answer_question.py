from src.commands.command_base import CommandBase


class AnswerQuestion(CommandBase):
    command_id = 2
    def __init__(self, answer_type:bool):
        self.answer_type = answer_type
        super().__init__()
    
    def to_dict(self):
        return {"answer_type":self.answer_type}
        
    @classmethod
    def from_dict(self, dct):
        return AnswerQuestion(answer_type=dct.get('answer_type'))