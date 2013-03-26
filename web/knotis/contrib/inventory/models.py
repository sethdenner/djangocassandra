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

        if slave.recipient_id != master.recipient_id:
            raise Exception('can not stack inventory unless recipients match')

        if slave.product_id != master.product_id:
            raise Exception('can not stack inventory unless products match')

        master.stock += slave.stock
        master.save()

        slave.deleted = True
        slave.save()

        return master

    def split(
        self,
        inventory,
        recipient,
        quantity,
        force=False
    ):
        if inventory.provider_id != inventory.recipient_id:
            raise Exception('can not split unowned inventory')

        if not force:
            if quantity > inventory.stock:
                raise Exception('quantity requested exceeds inventory stock')

        split = self.create(
            product=inventory.product,
            provider=inventory.provider,
            recipient=recipient,
            stock=quantity,
        )

        inventory.stock -= quantity
        inventory.save()

        return inventory, split

    def create_stack_from_product(
        self,
        identity,
        product
    ):
        return Inventory.objects.create(
            product=product,
            provider=identity,
            recipient=identity,
            stock=0.
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
        product,
        identity,
        offer=None
    ):
        inventory_stacks = self.objects.filter(
            product=product,
            provider=identity,
            recipient=identity
        )

        inventory_stack = None
        inventory_stack_offerless = None
        for stack in inventory_stacks:
            offer_items = stack.offer_item_set.all()
            if (
                not inventory_stack_offerless
                and not offer_items.count()
            ):
                inventory_stack_offerless = stack
                if offer:
                    continue

                else:
                    break

            if offer:
                for offer_item in offer_items:
                    if offer_item.offer_id == offer.id:
                        inventory_stack = offer_item.inventory
                        break

            if inventory_stack:
                break

        if not inventory_stack:
            if inventory_stack_offerless:
                inventory_stack = inventory_stack_offerless

            else:
                inventory_stack = (
                    Inventory.objects.create_stack_from_product(
                        identity,
                        product
                    )
                )

        return inventory_stack

    def get_provider_stack(
        self,
        inventory,
        offer=None
    ):
        return self.get_stack(
            inventory,
            inventory.provider,
            offer=offer
        )

    def get_recipient_stack(
        self,
        inventory,
        offer=None
    ):
        return self.get_stack(
            inventory,
            inventory.recipient,
            offer=offer
        )

    def get_participating_stacks(
        self,
        inventory,
        offer=None
    ):
        return (
            self.get_provider_stack(
                inventory,
                offer=offer
            ),
            self.get_recipient_stack(
                inventory,
                offer=offer
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

    objects = InventoryManager()

    def is_perishable(self):
        return False
