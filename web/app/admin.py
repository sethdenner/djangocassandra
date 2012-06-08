from django.contrib import admin

from models.knotis.accounts import Currency, AccountType, Account 
admin.site.register(Currency);
admin.site.register(AccountType);
admin.site.register(Account);

from models.knotis.businesses import Business
admin.site.register(Business)
