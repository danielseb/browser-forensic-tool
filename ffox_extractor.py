import os
import sqlite3
from pathlib import Path
import re

class ForensicImage:
    def __init__(self):
       self.path = self.get_mnt_pnt()
       self.os_type = self.detect_os()
       self.users_dir = self.detect_users_dir()
       self.home_dirs = self.detect_home_dirs()
       self.user_list = self.list_users()
       self.browser_dirs = self.get_browser_dirs()
    
    def get_mnt_pnt(self) -> str:
        while True:
            mnt_pnt = input('Enter mount point of forensic image: ')
            if re.match(r"^\/.+\/$", mnt_pnt) or re.match(r"^[a-zA-Z]{1}\:\.+\$", mnt_pnt):
                return mnt_pnt
            else:
                print(f'Incorrect format. Try: eg. /mount/point/ or D:\mount\point\\')
                continue

    def detect_os(self) -> str:
        if os.path.exists(f'{self.path}@home/') or os.path.exists(f'{self.path}home/'):
            return('Linux')
        elif os.path.exists(f'{self.path}Windows/'):
            return('Windows')
        elif os.path.exists(f'{self.path}System/Library/'):
            return('MacOS')
    
    def detect_users_dir(self):
        if self.os_type == 'Linux' and os.path.exists(f'{self.path}@home/'):
            return Path(f'{self.path}@home/')
        elif self.os_type == 'Linux' and os.path.exists(f'{self.path}home/'):
            return Path(f'{self.path}home/')
        elif self.os_type == 'Windows':
            return Path(f'{self.path}Windows/')
        elif self.os_type == 'MacOS':
            return Path(f'{self.path}System/Library/')

    def detect_home_dirs(self) -> list[str]:
       user_list = []
       user_list.extend([str(u) for u in self.users_dir.iterdir() if u.is_dir()])
       return user_list

    def list_users(self) -> list[str]:
        users = []
        users.extend([str(u.parts[-1]) for u in self.users_dir.iterdir() if u.is_dir()])
        return users

    def get_browser_dirs(self) -> dict[any]:
        browser_dirs =  {}
        for user in self.user_list:
            if self.os_type == 'Linux':
                browser_dirs[user] = {
                    "firefox": os.path.join(self.users_dir, user, ".mozilla", "firefox"),
                    "chrome": os.path.join(self.users_dir, user, ".config", "google-chrome", "Default") 
                }
            elif self.os_type == 'Windows':
                browser_dirs[user] = {
                    "firefox": os.path.join(self.users_dir, user, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles"),
                    "chrome": os.path.join(self.users_dir, user, "AppData", "Local", "Google", "Chrome", "User Data", "Default")
                }
            elif self.os_type == 'MacOS':
                browser_dirs[user] = {
                    "firefox": os.path.join(self.users_dir, user, "Library", "Application Support", "Firefox", "Profiles"),
                    "chrome": os.path.join(self.users_dir, user, "Library", "Application Support", "Google", "Chrome", "Default")
                }
        return browser_dirs
               
        
        

def extract_history(db_dir: str) -> list[any]:
    #this function works to query db without copying to temp dir
    QUERY = '''
                SELECT 
                moz_places.url AS url,
                moz_historyvisits.visit_date AS time
                FROM moz_places
                INNER JOIN moz_historyvisits
                ON moz_historyvisits.place_id == moz_places.id
                ORDER BY time DESC;
            '''

    db_file = os.path.join(db_dir, "places.sqlite")
    con = sqlite3.connect(f"file:{db_file}?mode=ro&immutable=1", uri=True)
    cur = con.cursor()
    results = cur.execute(QUERY).fetchall()
    con.close()
    return results

#print(extract_history('/mnt/forensics/@home/user/.mozilla/firefox/i1n33utz.default-esr/'))
image = ForensicImage()
print(image.os_type)
print(image.users_dir)
print(image.user_list)
print(image.browser_dirs)








