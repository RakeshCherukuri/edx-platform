"""
Fragment for rendering the course dates sidebar.
"""


from django.http import Http404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import get_language_bidi
from opaque_keys.edx.keys import CourseKey
from web_fragments.fragment import Fragment

from lms.djangoapps.courseware.courses import get_course_date_blocks, get_course_with_access
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView


class CourseDatesFragmentView(EdxFragmentView):
    """
    A fragment to important dates within a course.
    """
    template_name = 'course_experience/course-dates-fragment.html'

    def render_to_fragment(self, request, course_id=None, **kwargs):
        """
        Render the course dates fragment.
        """
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, 'load', course_key, check_if_enrolled=False)
        course_date_blocks = get_course_date_blocks(course, request.user, request, num_assignments=1)

        context = {
            'course_date_blocks': [block for block in course_date_blocks if block.title != 'current_datetime'],
            'dates_tab_link': reverse('dates', args=[course.id]),
        }
        html = render_to_string(self.template_name, context)
        dates_fragment = Fragment(html)
        self.add_fragment_resource_urls(dates_fragment)

        return dates_fragment


class CourseDatesFragmentMobileView(CourseDatesFragmentView):
    """
    A course dates fragment to show dates on mobile apps.

    Mobile apps uses WebKit mobile client to create and maintain a session with
    the server for authenticated requests, and it hasn't exposed any way to find
    out either session was created with the server or not so mobile app uses a
    mechanism to automatically create/recreate session with the server for all
    authenticated requests if the server returns 404.
    """
    _uses_pattern_library = False
    template_name = 'course_experience/mobile/course-dates-fragment.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        return super(CourseDatesFragmentMobileView, self).get(request, *args, **kwargs)

    def css_dependencies(self):
        """
        Returns list of CSS files that this view depends on.

        The helper function that it uses to obtain the list of CSS files
        works in conjunction with the Django pipeline to ensure that in development mode
        the files are loaded individually, but in production just the single bundle is loaded.
        """
        if get_language_bidi():
            return self.get_css_dependencies('style-mobile-rtl')
        else:
            return self.get_css_dependencies('style-mobile')
