from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase

from vtshop.utils import (
                            get_VAT_prices, 
                            min_length_8, 
                            contains_min_one_digit, 
                            contains_min_one_lower, 
                            contains_min_one_spec_char, 
                            contains_min_one_upper,
                            )


class UtilsTestCase(TestCase):

    def test_get_VAT_prices(self):

        # Arrange.
        price = Decimal(100)

        # Act.
        vat_amount, incl_vat_price = get_VAT_prices(price=price)
    
        # Assert.
        self.assertEqual(vat_amount, price * Decimal(0.2))
        self.assertEqual(incl_vat_price, price * (1 + Decimal(0.2)))


class PasswordCustomValidationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.fails_all_tests = "-"
        cls.too_short = "1234Ab&"
        cls.no_lower = "1234ABC&"
        cls.no_upper = "1234abc&"
        cls.no_digit = "ABCDabc&"
        cls.no_spec = "1234abcd"
        cls.acceptable = "1234Abc&"

    def test_min_length_8(self):

        # Act.
        try:
            min_length_8(self.fails_all_tests)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit avoir au moins 8 caractères.")
        
        # Act.
        try:
            min_length_8(self.too_short)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit avoir au moins 8 caractères.")

        # Assert.
        self.assertIsNone(min_length_8(self.acceptable))

    def test_contains_min_one_upper(self):

        # Act.
        try:
            contains_min_one_upper(self.fails_all_tests)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins une majuscule.")
        
        # Act.
        try:
            contains_min_one_upper(self.no_upper)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins une majuscule.")

        # Assert.
        self.assertIsNone(contains_min_one_upper(self.acceptable))

    def test_contains_min_one_lower(self):

        # Act.
        try:
            contains_min_one_lower(self.fails_all_tests)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins une minuscule.")
        
        # Act.
        try:
            contains_min_one_lower(self.no_lower)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins une minuscule.")

        # Assert.
        self.assertIsNone(contains_min_one_lower(self.acceptable))

    def test_contains_min_one_digit(self):

        # Act.
        try:
            contains_min_one_digit(self.fails_all_tests)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins un chiffre.")
        
        # Act.
        try:
            contains_min_one_digit(self.no_digit)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins un chiffre.")

        # Assert.
        self.assertIsNone(contains_min_one_digit(self.acceptable))

    def test_contains_min_one_spec_char(self):

        # Act.
        try:
            contains_min_one_spec_char(self.fails_all_tests)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins un caractère spécial parmi : @#&§!?_$£€%*^~()<>{}")
        
        # Act.
        try:
            contains_min_one_spec_char(self.no_spec)
        except Exception as e:
            # Assert.
            self.assertEqual(e.message, "Doit contenir au moins un caractère spécial parmi : @#&§!?_$£€%*^~()<>{}")

        # Assert.
        self.assertIsNone(contains_min_one_spec_char(self.acceptable))