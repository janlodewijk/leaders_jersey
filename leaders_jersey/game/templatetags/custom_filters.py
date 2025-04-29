from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def stage_label(stage_number):
    if stage_number == 0:
        return "Prologue"
    return f"{stage_number}"