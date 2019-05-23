from django.http import Http404, HttpResponse
from django.contrib.staticfiles import finders
from django.views.decorators.csrf import ensure_csrf_cookie
import mimetypes

@ensure_csrf_cookie
def index(request):
    """ Thin wrapper for the static index.html that adds the CSRF cookie."""
    filepath = request.path[1:] or "index.html"
    static_path = finders.find(filepath)
    if not static_path:
        raise Http404('Static file not found at: ' + filepath + '. Has the frontend been compiled?')
    with open(static_path, 'rb') as file:
        return HttpResponse(file, content_type=mimetypes.guess_type(filepath)[0])
