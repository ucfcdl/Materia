from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import redirect, render
from django.views.generic import View
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
import logging


def index(request, *args, **kwargs):
    context = {"title": "Welcome to Materia", "bundle_name": "homepage"}
    return render(request, "react.html", context)


def get_theme_overrides():
    # This function will be called before the help page is loaded.
    # You can use it to check for theme overrides.
    # Return a dictionary with the 'js' and 'css' keys if an override exists,
    # or None if no override exists.
    # For this example, we'll just return None.
    return None


def help(request):
    # Get the theme override, if any.
    theme_overrides = get_theme_overrides()

    # If a theme override exists, use its JS and CSS.
    # Otherwise, use the default JS and CSS.
    if theme_overrides:
        js_group = ["react", theme_overrides[0][1]["js"]]
        css_group = theme_overrides[0][1]["css"]
    else:
        js_group = ["react", "help"]
        css_group = "help"

    context = {"title": "Help", "bundle_name": "help", "css_group": css_group}

    return render(request, "react.html", context)


def handler404(request, exception):
    # Log the 404 URL
    logger = logging.getLogger(__name__)
    logger.warning("404 URL: %s", request.path)

    context = {"title": "404 Page Not Found", "bundle_name": "404"}

    # Render the template with context
    content = render(request, "react.html", context)

    # Return a 404 response with the rendered content
    return HttpResponseNotFound(content)


def handler500(request):
    return "ADSFASDF"

def create_context(title, bundle_name, js_group_name, css_group_name):
     # Get the theme override, if any.
    theme_overrides = get_theme_overrides()

    # If a theme override exists, use its JS and CSS.
    # Otherwise, use the default JS and CSS.
    if theme_overrides:
        js_group = ["react", theme_overrides[0][1]["js"]]
        css_group = theme_overrides[0][1]["css"]
    else:
        js_group = ["react", js_group_name]
        css_group = css_group_name

    context = {"title": title, "bundle_name": bundle_name, "css_group": css_group}

    return context

def user_get(request):
    """
    API Endpoint to get the current user.
    """
    if request.user.is_authenticated:
        user = request.user
        return HttpResponse(user, content_type="application/json")
    else:
        return HttpResponse('Not logged in')

class LoginView(View):
    """
    Build a non-SAML login page for users to authenticate.
    """
    def get(self, *args, **kwargs):  # pylint: disable=unused-argument
        if self.request.user.is_authenticated:
            return redirect("home page")
        else:
            context = create_context("Login", "login", "login", "login")
            return render(self.request, "react.html", context)

    def post(self, *args, **kwargs):
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        # Check the authentication backends for the user
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("home page")
        else:
            context = create_context("Login", "login", "login", "login")
            # Add an error message to the context
            context["ERR_LOGIN"] = "Invalid username or password"
            return render(self.request, "react.html", context)

class LogoutView(View):
    """
    Log the user out of the application.
    """

    def get(self, *args, **kwargs):  # pylint: disable=unused-argument
        logout(self.request)
        return redirect("home page")

    def post(self, *args, **kwargs):
        logout(self.request)
        return redirect("home page")