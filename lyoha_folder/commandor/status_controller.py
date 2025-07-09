from commandor.knowledge.knowledge import Knowledge


class StatusController():
    def __init__(self, knowledge:Knowledge):
        self.knowledge = knowledge
    
    def set_question(self, bilet_number, question_number, value):
        raise Exception("not implemented logic was called")

    def get_current_knowledge(self):
        return self.knowledge