class PassportApi(object):
    @staticmethod
    def _normal_redeem(purchase_pk):
        pass

    @staticmethod
    def _complex_redeem(
        collection_pk,
        page_number
    ):
        pass

    @staticmethod
    def redeem(
        purchase_pk=None,
        collection_pk=None,
        page_number=None
    ):
        if None is not purchase_pk:
            PassportApi._normal_redeem(purchase_pk)

        elif None is not collection_pk and None is not page_number:
            PassportApi._complex_redeem(
                collection_pk,
                page_number
            )

        else:
            raise Exception('Invalid Parameters.')

    @staticmethod
    def connect(
        transaction_colleciton_pk
    ):
        pass
