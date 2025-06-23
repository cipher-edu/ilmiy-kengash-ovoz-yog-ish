# apps/templatetags/voting_tags.py

from django import template

register = template.Library()

@register.simple_tag
def has_voted(voted_items, content_type_id, object_id):
    """
    Foydalanuvchi ma'lum bir obyekt uchun ovoz bergan yoki bermaganligini tekshiradi.
    voted_items - (content_type_id, object_id) kortezhlaridan iborat set.
    """
    return (content_type_id, object_id) in voted_items

@register.filter
def percent(value, total):
    try:
        value = float(value)
        total = float(total)
        if total == 0:
            return 0
        return int(round((value / total) * 100))
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
    
