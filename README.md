![](ghbnr.png)
===================

![](ghss.png)

This is a basic Pictochat-themed chatroom widget for a website.

I made this for my personal website, so it may be difficult to use in its current state as I am halfway done refactoring it.

## Usage

`pip install -r requirements.txt`

**Testing**

`flask --app chat run` (if you actually intend to use this please put it behind a reverse proxy and run it with `gunicorn`):

`gunicorn -w 1 --worker-class eventlet chat:app -b 127.0.0.1:5000`

If you are using Nginx, set up the appropriate rules:

```
location /chat {
  proxy_pass http://127.0.0.1:5000/
  ...
}

location /socket.io {
  proxy_pass http://127.0.0.1:5000/socket.io/
  ...
}
```

Special considerations need to be made if iframe embedding on another (sub)domain. You will need to set `Content-Security-Policy`, and some others:

```
server {
  ...
  add_header X-Frame-Options "ALLOW-FROM https://yourothercoolwebsite.net" always;
  add_header Content-Security-Policy "frame-ancestors 'self' https://www.yourothercoolwebsite.net https://yourothercoolwebsite.net;" always;

  ...
}
```

The above will probably be sufficient.
