import datetime as dt

import pytest
from pydantic import ValidationError
from stpmex.exc import InvalidRfcOrCurp

from speid.models import Account
from speid.types import Estado
from speid.validations import Account as AccountValidation


def test_account():
    account_validation = AccountValidation(
        nombre='Ricardo',
        apellido_paterno='Sánchez',
        cuenta='646180157063641989',
        rfc_curp='SACR891125M47',
        telefono='5567980796',
        fecha_nacimiento=dt.datetime(1989, 11, 25),
        pais_nacimiento='MX',
    )
    account = account_validation.transform()

    account.save()
    account_saved = Account.objects.get(id=account.id)

    assert account_saved.created_at is not None
    assert account_saved.updated_at is not None
    assert account.estado is Estado.created
    assert account_saved.nombre == account.nombre
    assert account_saved.apellido_paterno == account.apellido_paterno
    assert account_saved.apellido_materno == account.apellido_materno
    assert account_saved.cuenta == account.cuenta
    assert account_saved.rfc_curp == account.rfc_curp
    assert account_saved.telefono == account.telefono

    account.delete()


def test_account_bad_curp():
    with pytest.raises(ValidationError):
        AccountValidation(
            nombre='Ricardo',
            apellido_paterno='Sánchez',
            cuenta='646180157063641989',
            rfc_curp='S1CR891125HDFGHI01',
            telefono='5567980796',
            fecha_nacimiento=dt.date(1989, 11, 25),
            pais_nacimiento='MX',
        )


@pytest.mark.vcr
def test_create_account():
    account_validation = AccountValidation(
        nombre='Ricardo',
        apellido_paterno='Sánchez',
        cuenta='646180157069665325',
        rfc_curp='SACR891125HDFGHI01',
        telefono='5567980796',
        fecha_nacimiento=dt.datetime(1989, 11, 25),
        pais_nacimiento='MX',
    )

    account = account_validation.transform()

    account.save()

    account.create_account()

    assert account.estado is Estado.succeeded

    account.delete()


@pytest.mark.vcr
def test_create_account_failed():
    account_validation = AccountValidation(
        nombre='Ricardo',
        apellido_paterno='Sánchez',
        cuenta='646180157063641989',
        rfc_curp='SACR89112501',
        telefono='5567980796',
        fecha_nacimiento=dt.datetime(1989, 11, 25),
        pais_nacimiento='MX',
    )

    account = account_validation.transform()

    account.save()
    account_id = account.id

    with pytest.raises(InvalidRfcOrCurp):
        account.create_account()

    account = Account.objects.get(id=account_id)
    assert account.estado is Estado.error

    account.delete()
