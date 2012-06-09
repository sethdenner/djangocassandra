from django.contrib import admin

class AccountsAdmin(admin.ModelAdmin):
    pass
from models.knotis.accounts import Currency, AccountType, Account 
admin.site.register(Currency, AccountsAdmin);
admin.site.register(AccountType, AccountsAdmin);
admin.site.register(Account, AccountsAdmin);

class BusinessesAdmin(admin.ModelAdmin):
    pass
from models.knotis.businesses import Business
admin.site.register(Business, BusinessesAdmin)
