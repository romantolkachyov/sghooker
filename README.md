sghooker is a simple webservice consuming Sentry webhooks and redirecting them to the Google Chat.

This is just for fun and to play with new techs.

# Free-threading python support

The key experiment is to try nogil / free-threaded python.

There are some limitations in actual support:

* dependency-injector requires `PYTHON_GIL=0` set
* Docker image is based on 3.13 with GIL for a while
