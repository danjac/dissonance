NOTE: This is based on the article https://valberg.dk/django-sse-postgresql-listen-notify.html. I recommend reading this first for a good in-depth understanding of using PostgreSQL notifications with SSE.

The project is a simple Discord "clone" which allows users to run chat rooms. 

This is an experimental project to play with Server-Side Events, PostgreSQL NOTIFY/LISTEN and HTMX. The advantage of using PostgreSQL here with the latest async Django support (4.2+) is that we don't require an additional service e.g. Redis for managing channels, assuming you are already using a version of PostgreSQL that supports NOTIFY/LISTEN.

HTMX support is enabled through the [SSE extension](https://htmx.org/extensions/server-sent-events/).
