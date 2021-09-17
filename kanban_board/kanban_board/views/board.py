from kanban_board.models import Task, task
from pyramid.response import Response
from pyramid.view import view_config

"""
GET tasks - pobranie (content + section)
POST tasks - tworzenie
PATCH tasks/id - modyfikacja (content lub sekcja?)
DELETE tasks/id - usunięcie
"""


def mapper(task):
    return {
        "id": task.id,
        "content": task.content,
        "state": task.state
    }


class Board:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @view_config(route_name='task.base', request_method='GET', renderer='json')
    def task_list(self):
        if not self.logged_in:
            return Response(status=401, content_type='application/json; charset=UTF-8')

        return list(map(mapper, self.request.dbsession.query(Task).filter(Task.user_id == self.logged_in)))

    @view_config(route_name='task.base', request_method='POST', renderer='json')
    def create_task(self):
        if not self.logged_in:
            return Response(status=401, content_type='application/json; charset=UTF-8')

        task_data = self.request.json_body
        content = task_data.get("content")

        if not content or len(content) < 3:
            self.request.response.status = 400
            return {"error": "Zawartość zadania jest zbyt krótka!"}

        self.request.dbsession.add(Task(user_id=self.logged_in, content=content))

        return {}

    @view_config(route_name='task.update', request_method='PATCH', renderer='json')
    def update_task(self):
        if not self.logged_in:
            return Response(status=401, content_type='application/json; charset=UTF-8')

        task_id = self.request.matchdict["task_id"]

        if not task_id:
            return Response(status='400 not provided id', content_type='application/json; charset=UTF-8')

        task_data = self.request.json_body
        to_update = {}
        state = task_data.get("state")
        content = task_data.get("content")

        if state:
            state = state.upper()

            if state not in task.TYPES:
                return Response(status='400 bad state', content_type='application/json; charset=UTF-8')

            to_update[Task.state] = state

        if content:
            if len(content) < 3:
                return Response(status='400 too short content', content_type='application/json; charset=UTF-8')

            to_update[Task.content] = content

        if len(to_update) == 0:
            return Response(status='400 no update data', content_type='application/json; charset=UTF-8')

        result = self.request.dbsession.query(Task) \
            .filter(Task.id == task_id) \
            .filter(Task.user_id == self.logged_in) \
            .update(to_update)

        if result:
            return {}
        else:
            return Response(status=404, content_type='application/json; charset=UTF-8')

    @view_config(route_name='task.update', request_method='DELETE', renderer='json')
    def delete_task(self):
        print("delete")
        if not self.logged_in:
            return Response(status=401, content_type='application/json; charset=UTF-8')

        task_id = self.request.matchdict["task_id"]

        if not task_id:
            return Response(status='400 not provided id', content_type='application/json; charset=UTF-8')

        result = self.request.dbsession.query(Task) \
            .filter(Task.id == task_id) \
            .filter(Task.user_id == self.logged_in) \
            .delete()

        if result:
            return {}
        else:
            return Response(status=404, content_type='application/json; charset=UTF-8')
