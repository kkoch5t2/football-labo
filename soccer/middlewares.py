from django.http import HttpResponse
from django.template.loader import get_template

from myproject import settings


def get_ip(request):
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses:
        ip = forwarded_addresses.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class IpRestrictMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_ip(request)
        if ip in settings.ALLOWED_IP_BLOCKS:
            temp = get_template('ip_block/not_allowed_ip.html')
            result = temp.render({'ip': ip})
            return HttpResponse(result)

        response = self.get_response(request)

        return response
