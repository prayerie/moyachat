import psycopg2
import os 

conn = psycopg2.connect(host='localhost',
                        database=os.getenv('MOYACHAT_DB'),
                        user=os.getenv('MOYACHAT_DBUSER'),
                        password=os.getenv('MOYACHAT_DBPASS'))

cur = conn.cursor()

cur.execute('drop table if exists messages;')
cur.execute('drop table if exists users;')
cur.execute('drop table if exists ips;')

cur.execute('create table if not exists users (user_id varchar(8) unique not null primary key,'
            'reg_date timestamp default current_timestamp,'
            'last_seen_date timestamp default current_timestamp,'
            "last_ip cidr not null default '0.0.0.0'::cidr,"
            "last_nick text not null default '?',"
            "last_room text not null default 'main',"
            'locale text not null,'
            'n_messages integer not null default 0,'
            'ubanned boolean not null default false,'
            'is_uadmin boolean not null default false,'
            "banned_reason text not null default '*');"
            )

cur.execute('create table if not exists messages (id serial primary key,'
            'date timestamp default current_timestamp,'
            'user_id varchar(8) not null,'
            'content text not null,'
            "nick text not null default '?',"
            "ip cidr not null default '0.0.0.0'::cidr,"
            "locale varchar(2) not null default 'XX',"
            "room text not null default 'main',"
            'constraint fk_userid foreign key(user_id) references users(user_id),'
            'removed boolean not null default false);'
            )

cur.execute('create table if not exists ips (ip cidr primary key,'
            'ibanned boolean not null default false,'
            'is_iadmin boolean not null default false);')

conn.commit()
cur.close()
conn.close()
