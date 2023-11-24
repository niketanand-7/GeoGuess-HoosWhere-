from django import template
from django.urls import reverse

register = template.Library()
@register.simple_tag(takes_context=True)
def is_active(context, url_name):
    current_path = context['request'].path
    return 'active' if current_path == reverse(url_name) else ''