
class ActivityHandler():
    def __init__(self):
        self.activity = []

    def add_activity(self, activity):
        self.activity.append(activity)

    def clear_activity(self):
        self.activity = []
    
    def get_activity(self):
        return self.activity