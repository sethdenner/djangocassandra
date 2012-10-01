import datetime

from django.shortcuts import render
from django.conf import settings
from django.template import Context
from django.template.loader import get_template

from django.http import HttpResponseNotFound, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required

from app.models.transactions import Transaction
from app.models.businesses import Business


def render_highchart(
    options,
    request=None
):
    default_options = {}
    default_options.update(options)
    options = default_options
    
    if request:
        return render(
            request,
            'highchart.html',
            options
        )
    else:
        context = Context(options)
        highchart = get_template('highchart.html')
        return highchart.render(context) 


def render_daily_revenue_chart(
    business,
    request=None
):
    try:
        data = Transaction.objects.get_daily_revenue(business)
    
    except:
        data = None
    
    categories = []

    now = datetime.datetime.utcnow()
    start_date = now - datetime.timedelta(weeks=1)
    
    day_delta = 0
    while day_delta < 7:
        categories.append((
                start_date + datetime.timedelta(days=day_delta)
            ).strftime('%m/%d')
        )
        day_delta = day_delta + 1

    return render_highchart({
            'data': data,
            'categories': categories
        },
        request
    )


def render_weekly_revenue_chart(
    business,
    request=None
):
    try:
        data = Transaction.objects.get_weekly_revenue(business)
        
    except Exception, error:
        data = None
        
    categories = []
    now = datetime.datetime.utcnow()
    start_date = now - datetime.timedelta(weeks=7)

    week_delta = 0
    while week_delta < 7:
        categories.append((
                 start_date + datetime.timedelta(weeks=week_delta)
            ).strftime('%U')
        )
        week_delta = week_delta + 1
        
    return render_highchart({
            'data': data,
            'categories': categories
        },
        request
    )


def render_monthly_revenue_chart(
    business,
    request=None
):
    try:
        data = Transaction.objects.get_monthly_revenue(business)
        
    except:
        data = None
        
    categories = []
    now = datetime.datetime.utcnow()
    month_delta = 1
    while month_delta <= 12:
        categories.append((
                now + datetime.timedelta(
                    weeks=month_delta*4
                )
            ).strftime('%b')
        )
        month_delta = month_delta + 1
        
    return render_highchart({
            'data': data,
            'categories': categories
        },
        request
    )
    

@login_required
def get_revenue_chart(
    request,
    business_id=None,
    scope='daily'
):
    if None == business_id:
        try:
            business = Business.objects.get(user=request.user)

        except:
            business = None

    else:
        try:
            business = Business.objects.get(pk=business_id)

        except:
            business = None
    
    if None == business:
        return HttpResponseNotFound()
        
    scope = scope.lower()
    if 'daily' == scope:
        return render_daily_revenue_chart(
            business,
            request
        )
        
    elif 'weekly' == scope:
        return render_weekly_revenue_chart(
            business,
            request
        )
    
    elif 'monthly' == scope:
        return render_monthly_revenue_chart(
            business,
            request
        )

    else:
        return HttpResponseBadRequest('Scope must be one of: "daily", "weekly", "monthly".')
