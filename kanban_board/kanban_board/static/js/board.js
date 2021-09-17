async function requestAPI(url = "", requestMethod = "GET", data = null, parse = true) {
    response = await fetch(url, {
        method: requestMethod,
        body: data ? JSON.stringify(data) : null,
        headers: {
            'Content-Type': 'application/json'
                // 'Content-Type': 'application/x-www-form-urlencoded',
        }
    })

    if (parse) {
        return response.ok ? response.json() : null
    } else {
        return response
    }
}

function generateForm(content = "") {
    return `<form>
    <div class="form-group">
    <label>Treść zadania</label>
    <textarea rows="4" cols="25" class="content form-control">${content}</textarea>
    </div>
    </form>`
}

$(document).ready(function() {
    // Example starter JavaScript for disabling form submissions if there are invalid fields
    (function() {
        'use strict'

        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.querySelectorAll('.needs-validation')

        // Loop over them and prevent submission
        Array.prototype.slice.call(forms)
            .forEach(function(form) {
                form.addEventListener('submit', function(event) {
                    if (!form.checkValidity()) {
                        event.preventDefault()
                        event.stopPropagation()
                    }

                    form.classList.add('was-validated')
                }, false)
            })
    })()

    $(".board-container")
        .on("drop", function(event) {
            var target = $(event.target)
            if (!target.hasClass("board-container")) {
                return false
            }

            event.preventDefault()

            var data = event.originalEvent.dataTransfer.getData("task-id")
            event.target.appendChild(document.getElementById(data))

            requestAPI(`/tasks/${data}`, "PATCH", { "state": target.attr("id").toUpperCase() })
        })
        .on("dragover", function(event) {
            event.preventDefault()
        })

    setupBoard()

    $("#add-task").click(() => {
        $.confirm({
            title: 'Nowe zadanie',
            content: generateForm(),
            buttons: {
                submit: {
                    text: 'Utwórz',
                    btnClass: "btn-blue",
                    action: function() {
                        var content = this.$content.find(".content").val()

                        if (!content || content.length < 3) {
                            return false
                        }

                        requestAPI("/tasks", "POST", data = { "content": content }, parse = false)
                            .then(response => response.ok)
                            .then(() => setupBoard())
                    }
                },
                cancel: {
                    text: 'Anuluj'
                }
            },
            onContentReady: function() {
                var _this = this
                this.$content.find("form").on("submit", e => {
                    e.preventDefault()
                    _this.$$submit.trigger("click")
                })
            }
        })
    })
})

function setupBoard() {
    $("#todo").html('<h2 class="mb-3">Todo</h2>')
    $("#progress").html('<h2 class="mb-3">W trakcie</h2>')
    $("#done").html('<h2 class="mb-3">Gotowe</h2>')

    requestAPI("/tasks").then(tasks => {
        if (tasks == null) {
            location.reload()
            return
        }
        for (var i = 0; i < tasks.length; i++) {
            task = tasks[i]
            $(`#${task.state.toLowerCase()}`).append(createTask(task))
        }
    })
}

function createTask(task) {
    var htmlContent = task.content.replaceAll("\n", "<br>")
    return $("<section></section>")
        .html(htmlContent)
        .addClass("task")
        .attr("id", task.id)
        .data("task-id", task.id)
        .attr("draggable", true)
        .on("dragstart", event => {
            event.originalEvent.dataTransfer.setData("task-id", event.target.id)
        })
        .click(() => {
            $.alert({
                title: "Zadanie",
                content: htmlContent,
                buttons: {
                    edit: {
                        text: 'Edytuj',
                        btnClass: "btn-orange",
                        action: function() {
                            $.confirm({
                                title: 'Edycja zadania',
                                content: generateForm(task.content),
                                buttons: {
                                    update: {
                                        text: 'Zapisz',
                                        btnClass: "btn-orange",
                                        action: function() {
                                            var content = this.$content.find(".content").val()

                                            if (!content || content.length < 3) {
                                                return false
                                            }

                                            requestAPI(`/tasks/${task.id}`, "PATCH", data = { "content": content }, parse = false)
                                                // .then(response => response.ok)
                                                .then(response => {
                                                    if (response.status == 200) {
                                                        setupBoard()
                                                    } else {
                                                        $.alert({
                                                            title: "Błąd",
                                                            content: response.json().msg,
                                                            type: "red"
                                                        })
                                                    }
                                                })
                                        }
                                    },
                                    close: {
                                        text: 'Zamknij'
                                    }
                                }
                            })
                        }
                    },
                    delete: {
                        text: 'Usuń',
                        btnClass: "btn-red",
                        type: "orange",
                        action: function() {
                            $.confirm({
                                title: "Potwierdź",
                                content: "Czy na pewno chcesz usunąć te zadanie?",
                                buttons: {
                                    ok: {
                                        text: 'Tak',
                                        action: () => {
                                            requestAPI(`/tasks/${task.id}`, "DELETE", content = null, parse = false)
                                                .then(response => response.ok)
                                                .then(() => setupBoard())
                                        }
                                    },
                                    cancel: {
                                        text: 'Anuluj'
                                    }
                                }
                            })
                        }
                    },
                    close: {
                        text: 'Zamknij'
                    }
                }
            })
        })
}