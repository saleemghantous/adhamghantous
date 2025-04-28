from mongoengine import *


class Report(Document):
    alert_name = StringField()
    alert_type = StringField()
    alert_target=StringField()
    alert_date = StringField()
    call_id=ListField()
    attempts=IntField()
    data=DictField()
    
    
    def to_json(self):
        return {
            "alert_name": self.alert_name,
            "alert_type": self.alert_type,
            "alert_target":self.alert_target,
            "alert_date": self.alert_date,
            "alert_id":str(self.id),
            "call_id":self.call_id,
            "attempts":str(self.attempts),
            "data":self.data
        }
