import urllib.request, urllib.error
urls = [
    'http://127.0.0.1:8000/',
    'http://127.0.0.1:8000/student/signup/',
    'http://127.0.0.1:8000/teacher/signup/',
    'http://127.0.0.1:8000/student/login/',
    'http://127.0.0.1:8000/teacher/login/',
    'http://127.0.0.1:8000/forgot-password/',
    'http://127.0.0.1:8000/forgot-password/sent/',
    'http://127.0.0.1:8000/reset-password/',
    'http://127.0.0.1:8000/reset-password/success/',
    'http://127.0.0.1:8000/dashboard/',
]
for u in urls:
    try:
        resp = urllib.request.urlopen(u, timeout=5)
        print(u, '->', resp.status)
        print(resp.read(400).decode('utf-8', errors='replace')[:200])
    except urllib.error.HTTPError as e:
        print(u, '-> HTTPError', e.code)
    except Exception as e:
        print(u, '-> ERROR', e)
