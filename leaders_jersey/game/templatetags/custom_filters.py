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


STAGE_ICONS = {
    'Flat': 'flat.png',
    'Hills': 'hills.png',
    'Punch': 'punch.png',
    'Mountain': 'mountain.png',
    'Mountain climb finish': 'mountain_climb_finish.png',
    'Indiv. Time Trial': 'itt.png',
    'Team TT': 'ttt.png',
}

@register.filter
def stage_icon(stage_type):
    return STAGE_ICONS.get(stage_type, 'default.png')