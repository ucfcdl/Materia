from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.views.generic import TemplateView

from core.models import WidgetInstance


class ScoresView(TemplateView):
    template_name = 'react.html'

    def get_context_data(self, widget_instance_id, play_id):
        is_embedded = self.kwargs.get('is_embedded', False)
        is_preview = False # TODO see php
        token = self.kwargs.get('token')

        # Get widget instance
        instance = WidgetInstance.objects.filter(pk=widget_instance_id).first()
        if not instance:
            return HttpResponseNotFound()

        # Verify user is able to play this widget
        if not instance.playable_by_current_user():
            # TODO:
            # Session::set_flash('notice', 'Please log in to view your scores.');
            # Response::redirect(Router::get('login').'?redirect='.urlencode(URI::current()));
            return HttpResponseForbidden()

        # Set up context and return
        js_globals = {
            "IS_EMBEDDED": is_embedded,
            "IS_PREVIEW": is_preview,
        }

        if token:
            js_globals["LAUNCH_TOKEN"] = token


        # TODO: insert support inline info - see php

        return {
            "title": "Score Results",
            "js_resources": ["dist/js/scores.js"],
            "css_resources": ["dist/css/scores.css"],
            "js_global_variables": js_globals
        }