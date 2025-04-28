from .config import *
from .UserObj import *

def check_admin(username,password):
    if(username=="admin" and password==config["admin_password"]):
        return True
    return False


def check_user(userId,password):
    user = User.objects(userId=userId,password=password).first()
    if (user):
        return True
    return False
