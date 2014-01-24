from django.shortcuts import redirect

from knotis.contrib.legacy.models import (
    QrcodeIdMap
)


def qrcode_redirect(
    request,
    legacy_qrcode_id
):
    qrcode = None
    try:
        id_map = QrcodeIdMap.objects.get(old_id=legacy_qrcode_id)
        qrcode = id_map.new_qrcode
    except:
        pass

    if None == qrcode:
        # can't redirect properly. drop on main page.
        return redirect('/')

    return redirect(
        '/qrcode/%s/' % (qrcode.id),
        premanent=True
    )
