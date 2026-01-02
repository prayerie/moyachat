from time import time
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .. import socketio
import os
import db
import geocoder


def get_ip(req):
    if 'X-Forwarded-For' in req.headers:
        return req.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        return req.remote_addr or '0.0.0.0'


@socketio.on('mdel', namespace='/')
def mdel(messageId):
    conn = db.get_conn()
    with conn.cursor() as c:
        author = db.get_author(c, messageId['mid'])

        if session.get('uid', '') != '' and (db.is_admin(c, session.get('uid', '')) or author == session.get('uid', '')):
            db.del_msg(c, messageId['mid'])
            emit('deleted', {
                'mid': messageId['mid'],
            }, to=session.get('room').replace('/', ''))
        else:
            db.ban(session['uid'], "tryhack")
            print("Unauthorised delete")


@socketio.on('joined', namespace='/')
def joined(message):
    join_room(session.get('room').replace('/', ''))

@socketio.on('text', namespace='/')
def text(message):
    rm = session.get('room').replace('/', '')
    if (len(message['msg']) > 280 or len(message['name']) > 24) or len(message['msg']) == 0 or len(message['name']) == 0 or "[br]" in message['msg']:
        return
    if os.environ('BADWORD1') in message['msg'].lower() or "TESTBAN123" in message['msg']:
        db.ban(session['uid'], "racist")
        return
    if not db.is_admin(session['uid']):
        if db.get_spamrate(20, session['uid']) >= 10:
            db.ban(session['uid'], "flood")
            return
        if db.get_spamrate(20, session['uid']) >= 10:
            return
        if db.get_spamrate(5, session['uid']) >= 3:
            return

    if message['msg'][0] == '!':
        return

    shadowbanned = db.is_banned(session['uid'])
    if shadowbanned:
        return

    conn = db.get_conn()
    cur = conn.cursor()
    # IP is stored so I can reliably ban racists and spammers
    # the geocoding thing isn't necessary; I wanted to add in future
    # maybe a little country flag next to each person's message
    cur.execute('insert into messages(user_id, content, ip, nick, locale, room)'
                'values (%s, %s, %s, %s, %s, %s) returning id;',
                (session['uid'], message['msg'], get_ip(request), message['name'], geocoder.ip(get_ip(request)).current_result.country or "XX", session.get('room').replace('/', '')))
    mid = cur.fetchone()[0]
    cur.execute(
        'update users set n_messages = n_messages + 1 where user_id = %s', (session['uid'],))
    cur.execute('update users set last_nick = %s, last_room = %s where user_id = %s',
                (message['name'], rm, session['uid'], ))
    conn.commit()
    cur.close()
    conn.close()
    session['name'] = message['name']

    emit('message', {
        'msg': f"{message['msg']}",
        'uid': session['uid'],
        'nick': message['name'],
        'mmid': mid
    }, to=rm)


@socketio.on('left', namespace='/')
def left(message):
    rm = session.get('room').replace('/', '')
    leave_room(rm)
