import psycopg2
import os
from dotenv import load_dotenv
from typing import List

# todo finish refactor
class MessageDB(object):
    def __init__(self):
        load_dotenv()
        self.conn: psycopg2.extensions.connection = self.get_conn()
        self.cursor: psycopg2.extensions.cursor = self.conn.cursor()

    def get_conn(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(host='localhost',
                                database=os.getenv('MOYACHAT_DB'),
                                user=os.getenv('MOYACHAT_DBUSER'),
                                password=os.getenv('MOYACHAT_DBPASS'))


def get_hist(c: psycopg2.extensions.cursor) -> List:
    with c:
        c.execute(
            'select * from messages where removed = false order by date asc;')
        return c.fetchall()

def is_admin(c: psycopg2.extensions.cursor, uid) -> bool:
    with c:
        c.execute(
            'select is_uadmin, last_ip from users where user_id = %s;', (uid,))
        res = c.fetchone()
        is_uadmin = res[0]
        c.execute('select is_iadmin from ips where ip = %s;', (res[1],))
        is_iadmin = c.fetchone()[0]
        return is_uadmin or is_iadmin or False
    
def unban(c: psycopg2.extensions.cursor, uid):
    with c:
        c.execute('update users set ubanned = false where user_id = %s;', (uid,))
        c.execute('update ips set ibanned = false where ip in '
                  '(select u.last_ip '
                  'from users u where u.user_id = %s);', (uid,))

def get_spamrate(c: psycopg2.extensions.cursor, secs, uid):
    with c:
        c.execute('select count(*) from messages '
        "where date > current_timestamp - interval '%s seconds' and "
        'user_id = %s;', (secs, uid,))
        cc = c.fetchone()
        if cc:
            return cc[0]
        else:
            return 0
        
def is_banned(c: psycopg2.extensions.cursor, uid):
    with c:
        c.execute('select ubanned, last_ip from users where user_id = %s;', (uid,))
        res = c.fetchone()
        is_ubanned = res[0]
        c.execute('select ibanned from ips where ip = %s;', (res[1],))
        is_ibanned = c.fetchone()[0]
        return is_ibanned or is_ubanned or False
    
def is_admin(c: psycopg2.extensions.cursor, uid):
    with c:
        c.execute('select is_uadmin, last_ip from users where user_id = %s;', (uid,))
        res = c.fetchone()
        is_uadmin = res[0]
        c.execute('select is_iadmin from ips where ip = %s;', (res[1],))
        is_iadmin = c.fetchone()[0]
        return is_uadmin or is_iadmin or False

def del_msg(c: psycopg2.extensions.cursor, mid):
    with c:
        c.execute('update messages set removed = true where id = %s;', (mid,))

def get_author(c: psycopg2.extensions.cursor, mid) -> str:
    c.execute('select user_id from messages where id = %s;', (mid,))
    return c.fetchone()[0]

def adminme(c: psycopg2.extensions.cursor, uid):
    print(f"Set uadmin true for {uid}")
    
    with c:
        c.execute('update users set is_uadmin = true where user_id = %s;', (uid,))

def ban(c: psycopg2.extensions.cursor, uid, reason="Unknown"):
    with c:
        c.execute('update users set ubanned = true, banned_reason = %s where user_id = %s;', (reason, uid,))
        c.execute('update ips set ibanned = true where ip in '
                  '(select u.last_ip '
                  'from users u where u.user_id = %s);', (uid,))
        c.execute('update messages set removed = true where user_id = %s', (uid,))
