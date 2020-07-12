from py4web.core import action

@action("index")
@action.uses("index.html")
def index():
    return dict()
