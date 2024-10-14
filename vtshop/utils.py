"""A utility module for vtshop app."""

import string, random, re
from decimal import Decimal

from django import forms

VAT_FRANCE = 0.2

############################
##### Reference number #####
############################


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    """Generate a random string of 10 characters"""

    return "".join(random.choice(chars) for i in range(size))


def unique_ref_number_generator(instance):
    """Make unique reference number."""
    ref_number = random_string_generator()

    Klass = instance.__class__

    qs_exists = Klass.objects.filter(ref_number=ref_number).exists()
    if qs_exists:
        return unique_ref_number_generator(instance)
    return ref_number


###############################
##### Registration number #####
###############################


def random_reg_number_generator(size=4, chars=string.digits):
    """Generate a random string of 4 digits"""

    return "".join(random.choice(chars) for i in range(size))


def unique_reg_number_generator(instance):
    """Make unique registration number."""
    reg_number = random_reg_number_generator()

    Klass = instance.__class__

    qs_exists = Klass.objects.filter(reg_number=reg_number).exists()
    if qs_exists:
        return unique_reg_number_generator(instance)
    return reg_number


#######################


def get_VAT_prices(price):
    """
    Calculate VAT and incl. VAT prices from HT price.

    Args:
        price (Decimal): price VAT excl.

    Returns:
        vat_amount (Decimal),
        incl_vat_price (Decimal).
    """

    vat = Decimal(VAT_FRANCE)
    vat_amount = vat * price
    incl_vat_price = (1 + vat) * price

    return vat_amount, incl_vat_price


######################################
##### CUSTOM PASSWORD VALIDATORS #####
######################################


def min_length_8(value):
    """Check if value has min length of 8 characters."""

    if len(value) < 8:
        raise forms.ValidationError("Doit avoir au moins 8 caractères.")


def contains_min_one_upper(value):
    """Check if value contains at least one upper case character."""

    for char in value:
        if char.isupper():
            return

    raise forms.ValidationError("Doit contenir au moins une majuscule.")


def contains_min_one_lower(value):
    """Check if value contains at least one lower case character."""

    for char in value:
        if char.islower():
            return

    raise forms.ValidationError("Doit contenir au moins une minuscule.")


def contains_min_one_digit(value):
    """Check if value contains at least one digit character."""

    for char in value:
        if char.isdigit():
            return

    raise forms.ValidationError("Doit contenir au moins un chiffre.")


def contains_min_one_spec_char(value):
    """Check if value contains at least one special character."""

    p = re.compile(r"[@#&§!?_$£€%*^~()<>{}]")
    if p.search(value):
        return

    raise forms.ValidationError(
        "Doit contenir au moins un caractère spécial parmi : @#&§!?_$£€%*^~()<>{}"
    )