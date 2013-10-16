from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickFloatField,
    QuickBooleanField
)
from knotis.contrib.identity.models import (
    Identity
)

from knotis.contrib.product.models import (
    Product
)


class InventoryManager(QuickManager):
    '''
    The method "stack" merges two inventories into one.
    Note that this method deletes the slave stack so
    this might not be the method you want if you plan on
    still using that inventory for other things.
    '''
    def stack(
        self,
        slave,
        master
    ):
        if master.provider_id != master.recipient_id:
            raise Exception('can not stack onto unstacked inventory')

        if (
            slave.recipient_id != master.recipient_id and
            slave.provider_id != master.recipient_id
        ):
            raise Exception(
                'can not stack inventory unless participants match'
            )

        if slave.product_id != master.product_id:
            raise Exception('can not stack inventory unless products match')

        # if slave inventory is perishable don't stack it.
        # That inventory is no longer tracked by our system.
        if not slave.perishable:
            master.stock += slave.stock
            master.save()

        slave.deleted = True
        slave.save()

    def split(
        self,
        inventory,
        recipient,
        quantity,
        force=False
    ):
        if inventory.provider_id != inventory.recipient_id:
            raise Exception('can not split unstacked inventory')

        if not force and not inventory.unlimited:
            if quantity > inventory.stock:
                raise Exception('quantity requested exceeds inventory stock')

        split = self.create(
            product=inventory.product,
            provider=inventory.provider,
            recipient=recipient,
            stock=quantity,
            price=inventory.price
        )

        if not inventory.unlimited:
            inventory.stock -= quantity
            inventory.save()

        return split

    def create_stack_from_product(
        self,
        identity,
        product,
        price=0.,
        stock=0.,
        unlimited=False,
        get_existing=False
    ):
        existing = None
        if get_existing:
            existing_stacks = Inventory.objects.filter(
                provider=identity,
                recipient=identity,
                product=product
            )

            for e in existing_stacks:
                if not e.offeritem_set.all():
                    existing = e
                    break

        if existing:
            # update existing stack columns
            existing.price = price
            existing.stock += stock
            existing.unlimited = unlimited
            existing.save()
            return existing

        else:
            return Inventory.objects.create(
                product=product,
                provider=identity,
                recipient=identity,
                price=price,
                stock=stock,
                unlimited=unlimited
            )

    def create_stack_from_inventory(
        self,
        identity,
        inventory
    ):
        return self.create_stack_from_product(
            identity,
            inventory.product
        )

    def get_stack(
        self,
        identity,
        product,
        create_empty=False
    ):
        inventory_stacks = self.filter(
            product=product,
            provider=identity,
            recipient=identity
        )

        inventory_stack = None
        for stack in inventory_stacks:
            offer_items = stack.offeritem_set.all()
            if offer_items.count():
                continue

            if stack.product_id == product.id:
                inventory_stack = stack
                break

        if not inventory_stack and create_empty:
            inventory_stack = (
                Inventory.objects.create_stack_from_product(
                    identity,
                    product
                )
            )

        return inventory_stack

    def get_provider_stack(
        self,
        inventory
    ):
        return self.get_stack(
            inventory.provider,
            inventory.product
        )

    def get_recipient_stack(
        self,
        inventory
    ):
        return self.get_stack(
            inventory.recipient,
            inventory.product
        )

    def get_participating_stacks(
        self,
        inventory
    ):
        return (
            self.get_provider_stack(
                inventory
            ),
            self.get_recipient_stack(
                inventory
            )
        )


class Inventory(QuickModel):
    product = QuickForeignKey(Product)
    provider = QuickForeignKey(
        Identity,
        related_name='inventory_provider'
    )
    recipient = QuickForeignKey(
        Identity,
        related_name='inventory_recipient'
    )
    stock = QuickFloatField()
    price = QuickFloatField()
    unlimited = QuickBooleanField()
    perishable = QuickBooleanField()

    objects = InventoryManager()
