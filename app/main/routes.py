from flask import session, render_template, request
from . import main
from db import MessageDB
import uuid
import hashlib
import geocoder
import requests

def get_ip(req):
    if 'X-Forwarded-For' in req.headers:
        return req.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        return req.remote_addr or '0.0.0.0'

def get_location(ip):
    response = requests.get(f'https://ipapi.co/{ip}/json/').json()
    location_data = {
        "ip": ip,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data

# generate a sorta random uid based on ipv4
def gen_id(ip):
    return hashlib.sha256(ip.encode('utf-8')).hexdigest()[:4] + str(uuid.uuid4())[:4]


@main.route('/')
def index():
    rm = request.args.get('room', 'main').replace('/', '')
    client_addr = get_ip(request)
    if 'uid' in session:
        # print("Has uid %s" % session['uid'])
        pass
    else:
        session['uid'] = gen_id(client_addr)
    conn = db.get_conn()
    cur = conn.cursor()
    iso3166code = geocoder.ip(get_ip(request)).current_result.country or "XX"
    cur.execute('insert into users(user_id, last_ip, last_seen_date, locale)'
                'values (%s, %s, current_timestamp, %s)'
                'on conflict(user_id) do update set '
                'last_ip = excluded.last_ip, '
                'last_seen_date = excluded.last_seen_date;',
                (session['uid'], client_addr, iso3166code))
    cur.execute('insert into ips(ip, ibanned) values(%s, false)'
                'on conflict(ip) do update set '
                'ip = excluded.ip;', (client_addr,))
    conn.commit()
    cur.execute('select last_nick from users where user_id = %s;',
                (session['uid'],))
    nick = cur.fetchone()[0]
    if nick != '?':
        session['name'] = nick

    if 'name' not in session:
        session['name'] = ""
    session['room'] = rm
    message_hist = db.get_hist()
    cur.close()
    conn.close()

    filtered_hist = list(filter(lambda x: x[7] == rm, message_hist))
    op = False
    sessuid = session.get('uid', '')
    if sessuid != '':
        op = is_admin(sessuid)
    return render_template('chat.html', name=session['name'], room=rm, history=filtered_hist[:200], sess=session['uid'], is_op=is_admin(session.get('uid', 'ffffffff')))
