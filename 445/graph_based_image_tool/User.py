import uuid
import hashlib

class User:

    def __init__(self,username, email, fullname, passwd):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd

        self.__token = None
        
        self.curr_graph = None

    def __str__(self) -> str:
        return "{\n\t" \
            + "Username : " + self.username + "\n\t" \
            + "Email : " + self.email + "\n\t" \
            + "Fullname : " + self.fullname + "\n\t" \
            + "Password : " + self.passwd + "\n" \
            + "}"

    # GETTERS AND SETTERS
    def get(self):
        return self

    def get_username(self):
        return self.username
    
    def get_email(self):
        return self.email

    def get_fullname(self):
        return self.fullname
    
    def get_passwd(self):
        return self.passwd
    
    def set_username(self,username):
        self.username = username
    
    def set_email(self,email):
        self.email = email
    
    def set_fullname(self,fullname):
        self.fullname = fullname

    def set_passwd(self,passwd):
        self.passwd = passwd

    def set_curr_graph(self,graph):
        self.curr_graph = graph

    def get_curr_graph(self):
        return self.curr_graph
    

    def delete(self):
        del self

    def auth(self, plainpass):
        return self.passwd == hashlib.sha256(plainpass.encode()).hexdigest()

    def login(self):
        self.__token = uuid.uuid4()
        return self.__token

    def checksession(self,token):
        return self.__token == token

    def logout(self):
        self.__token = None