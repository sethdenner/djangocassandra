from django.contrib import admin

from knotis.models.accounts import Currency, AccountType, Account 
admin.site.register(Currency);
admin.site.register(AccountType);
admin.site.register(Account);

from knotis.models.businesses import Business
admin.site.register(Business)
