"""An authorisation utilities module for vtshop app."""

from vtshop.models import User
from django.contrib.auth.mixins import UserPassesTestMixin


######################################
##### ROLE CONTROL CUSTOM MIXINS #####
######################################


class TestIsCustomerMixin(UserPassesTestMixin):
    """Mixin class controling access to user with CUSTOMER role."""

    def test_func(self):
        return self.request.user.role == "CUSTOMER"


class TestIsEmployeeMixin(UserPassesTestMixin):
    """Mixin class controling access to user with EMPLOYEE role."""

    def test_func(self):
        return self.request.user.role == "EMPLOYEE"


class TestIsCustomerOrEmployeeMixin(UserPassesTestMixin):
    """Mixin class controling access to user with EMPLOYEE role."""

    def test_func(self):
        return (
            self.request.user.role == "CUSTOMER" or self.request.user.role == "EMPLOYEE"
        )


class TestIsAdministratorMixin(UserPassesTestMixin):
    """Mixin class controling access to user with ADMINISTRATOR role."""

    def test_func(self):
        return self.request.user.role == "ADMINISTRATOR"