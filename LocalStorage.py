class LocalStorage:
    def __init__(self, driver) -> None:
        self.driver = driver
    
    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")
    
    def set_auth(self, dc2_auth, user_auth):
        self.driver.execute_script("window.localStorage.setItem('dc2_auth_key', arguments[0]);", dc2_auth)
        self.driver.execute_script("window.localStorage.setItem('user_auth_key', arguments[0]);", user_auth)
