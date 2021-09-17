"""
GET tasks - pobranie (content + section)
POST tasks - tworzenie
PATCH tasks/id - modyfikacja (content lub sekcja?)
DELETE tasks/id - usunięcie
"""


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=0)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('task.base', '/tasks')
    config.add_route('task.update', '/tasks/{task_id}')
