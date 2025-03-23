import sqlite3
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import os


def find_home_dir(image_mnt_pnt):
    possible_home_dirs = [Path(f"{image_mnt_pnt}home"), Path(f"{image_mnt_pnt}@home")]
    for dir in possible_home_dirs:
        if dir.exists():
            return dir

def find_ff_db_dirs(home_dir):
    home_dir = Path(home_dir)
    ff_db_dirs = []
    for user_dir in home_dir.iterdir():
        if not user_dir.is_dir():
            continue
        ff_dir = user_dir / ".mozilla/firefox"
        if not ff_dir.exists():
            continue
        ff_db_dirs.extend([str(p) for p in ff_dir.iterdir() if p.is_dir() and ".default-" in p.name])
        return ff_db_dirs

def extract_history(temp_dir):
    QUERY = '''SELECT 
                moz_places.url AS url,
                moz_historyvisits.visit_date AS time
                FROM moz_places
                INNER JOIN moz_historyvisits
                ON moz_historyvisits.place_id == moz_places.id
                ORDER BY time DESC;'''

    new_db_file = os.path.join(temp_dir, 'places.sqlite')
    con = sqlite3.connect(new_db_file)
    df = pd.read_sql_query(QUERY, con)
    df.to_csv('./test.csv', index=False, header=True)
    con.close()

def copy_ff_dir(ff_db_dirs, temp_dir):
    for dir in ff_db_dirs:
        try:
            shutil.copytree(dir, temp_dir, dirs_exist_ok=True)
        except Exception as e:
            print(f"Error during copy: {e}")

def main():

    temp_dir = tempfile.mkdtemp()
    image_mnt_pnt = input('Enter mount point of forensic image: ')
    home_dir = find_home_dir(image_mnt_pnt)

    try:
        ff_db_dirs = find_ff_db_dirs(home_dir)
        copy_ff_dir(ff_db_dirs, temp_dir)
        extract_history(temp_dir) 
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()







