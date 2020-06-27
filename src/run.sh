ps -ef | grep puppet_backend.asgi:application | grep -v grep | awk '{print $2}' | xargs kill -9
source /home/yangjun/venvs/django/bin/activate
nohup daphne -b 0.0.0.0 -p 8888 --proxy-headers puppet_backend.asgi:application &
