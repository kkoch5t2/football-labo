from django import template
from math import modf
from soccer.models import(
    CustomUser,
    Connection,
)

register = template.Library()
 
@register.filter(name="following_flg")
def following_flg(follower, following):
    connected = Connection.objects.filter(follower__username=follower, following__username=following).exists()
    if connected:
        return True
    else:
        return False