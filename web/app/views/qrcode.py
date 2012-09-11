from django.shortcuts import redirect

from app.models.qrcodes import Qrcode

def scan(request, qrcode_id):
    qrcode = None
    try:
        qrcode = Qrcode.objects.get(pk=qrcode_id)
    except:
        pass

    if not qrcode:
        return redirect('/')

    return qrcode.scan()
