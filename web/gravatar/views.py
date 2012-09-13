import md5

def avatar(
    email,
    s=32,
    d='mm',
    r='g',
    img=False,
    img_attrs={}
):
    url = 'http://www.gravatar.com/avatar/'
    url += md5.new(email.lower().strip()).hexdigest()
    url += '?s=%i&d=%s&r=%s' % (s, d, r)

    if img:
        url = '<img src="' + url + '"'
        for key in img_attrs:
            url += ' ' + key + '="' + img_attrs[key] + '"'
        url += ' />'

    return url
