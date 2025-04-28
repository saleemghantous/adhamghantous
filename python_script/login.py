from .authentication import *
from .UserObj import *

def login_request(data):
    if(check_admin(data["username"],data["password"])):
        return {"firstName":"מנהל המערכת","admin":True,"loginStatus":True}
    return {"firstName":"","admin":False,"loginStatus":False}