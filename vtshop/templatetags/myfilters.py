"""Custom template tag filters module."""

from django import template

register = template.Library()

@register.filter
def addclass(value, arg):
    """Typically add some CSS classes to a widget."""

    return value.as_widget(attrs={'class': arg})