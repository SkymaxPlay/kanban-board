from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import view_config

from ..models import User
from ..security import get_user_data, check_password, hash_password


class Root:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid
        self.user_data = get_user_data(request) if self.logged_in else None

    @view_config(route_name='home', renderer='kanban_board:templates/home.jinja2')
    def home(self):
        if not self.logged_in:
            return HTTPFound(self.request.route_url("login"))

        return {"login": self.logged_in}

    @view_config(route_name="login", renderer="kanban_board:templates/login.jinja2")
    def login(self):
        if self.logged_in:
            return HTTPFound(self.request.route_url("home"))

        error = ""

        if "form.submitted" in self.request.params:
            login = self.request.params.get("form.login")
            password = self.request.params.get("form.password")

            response = self.request.dbsession.query(User) \
                .filter(User.username == login).first()

            if response is not None and check_password(password=password, hashed_password=response.password):
                headers = remember(self.request, response.id)
                return HTTPFound(location=self.request.route_url("home"), headers=headers)
            else:
                error = "Błędny login lub hasło!"

        return {"action_url": self.request.route_url("login"), "error": error}

    @view_config(route_name="register", renderer="kanban_board:templates/register.jinja2")
    def register(self):
        if self.logged_in:
            return HTTPFound(self.request.route_url("home"))

        if "form.submitted" in self.request.params:
            login = self.request.params.get("form.login")
            password = self.request.params.get("form.password")
            password2 = self.request.params.get("form.password2")

            if not login or not password:
                return {"action_url": self.request.route_url("register"), "error": "Wprowadź login oraz hasło!"}

            if password != password2:
                return {"action_url": self.request.route_url("register"), "error": "Hasła nie są identyczne!"}

            response = self.request.dbsession.query(User) \
                .filter(User.username == login).first()

            if response is not None:
                return {"action_url": self.request.route_url("register"),
                        "error": "Użytkownik o takiej nazwie już istnieje!"}

            self.request.dbsession.add(User(username=login, password=hash_password(password)))

            return HTTPFound(self.request.route_url("home"))

        return {"action_url": self.request.route_url("register"), "error": ""}

    @view_config(route_name="logout")
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url("login"), headers=headers)
