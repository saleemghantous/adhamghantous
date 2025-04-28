from mongoengine import *


class User(Document):
    first_name = StringField()
    last_name = StringField()
    role = DictField()
    phone = StringField()
    address = StringField()
    department=DictField()
    first_phase=StringField()
    second_phase=StringField()
    
    def to_json(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "phone": self.phone,
            "address": self.address,
            "department": self.department,
            "first_phase":self.first_phase,
            "second_phase":self.second_phase
        }
