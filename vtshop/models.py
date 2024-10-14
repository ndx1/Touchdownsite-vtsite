from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import (
    get_VAT_prices,
    unique_ref_number_generator,
    unique_reg_number_generator,
)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    ADMINISTRATOR = "ADMINISTRATOR"
    EMPLOYEE = "EMPLOYEE"
    CUSTOMER = "CUSTOMER"

    ROLE_CHOICES = (
        (ADMINISTRATOR, "Admin"),
        (EMPLOYEE, "Employee"),
        (CUSTOMER, "Customer"),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=CUSTOMER)
    company = models.CharField(max_length=200, null=True)
    reg_number = models.CharField(max_length=4, null=True)

    def __str__(self):
        return self.first_name


class CustomerAccount(models.Model):
    "Our customer account model."

    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)
    customer = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    employee_reg = models.CharField(max_length=4, null=True)

    def set_cart(self):
        """Assign a cart to customer account"""

        try:
            self.cart
        except ObjectDoesNotExist:
            Cart.objects.create(customer_account=self)

    def _choose_related_employee(self):
        """Choose employee with least related customers."""

        employees = User.objects.filter(role="EMPLOYEE")

        if employees.count() == 0:  # Abort if no employee exists.
            return

        employee = employees[0]
        count = CustomerAccount.objects.filter(employee_reg=employee.reg_number).count()

        for e in employees:
            # Checking for reg_number should be usefull only at dev time. In production, every employee should have a reg_number.
            if e.reg_number is None:
                e.reg_number = unique_reg_number_generator(e)
                e.save()
                return e.reg_number

            customers_count = CustomerAccount.objects.filter(
                employee_reg=e.reg_number
            ).count()
            if customers_count < count:
                count = customers_count
                employee = e

        return employee

    def set_employee_reg_number(self):
        """Assign related employee reg_nubmer."""

        related_employee = self._choose_related_employee()

        if related_employee is not None:  # Abort if no employee exists.
            self.employee_reg = related_employee.reg_number
            self.save()

    def set_conversation(self, subject, customer):
        """Create a conversation with customer and related employee as participants."""

        related_employee = User.objects.get(reg_number=self.employee_reg)

        # Abort if this conversation is already set.
        if (
            Conversation.objects.filter(participants=customer)
            .filter(participants=related_employee)
            .exists()
        ):
            return

        new_conversation = Conversation.objects.create(subject=subject)
        new_conversation.participants.add(customer)

        new_conversation.participants.add(related_employee)

        new_conversation.save()


class Category(models.Model):
    """This is our Category model, aimed to group and filter Products."""

    name = models.CharField(
        max_length=200, unique=True
    )  # The default form widget for this field is a TextInput.
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Product(models.Model):
    """This is our Product model."""

    class Meta:
        ordering = ["-date_created"]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(null=False, unique=True)
    date_created = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="product_img/%Y/%m/%d/", blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )

    def get_absolute_url(self):
        return reverse("vtshop:product-detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Cart(models.Model):
    """This is our cart model."""

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customer_account = models.OneToOneField(
        CustomerAccount, on_delete=models.CASCADE, null=True
    )

    def calculate_total_price(self):
        """
        A utility method to summ up the prices of all the line items in cart.
        Populates total_price field.
        """

        self.total_price = 0

        for li in LineItem.objects.filter(cart=self):
            if li.cart is not None:
                self.total_price += li.price

    def add_line_item(self, product, quantity):
        """
        Add a line item to the cart, update total price.
        Essentially accessed from product view.
        """

        li, created = LineItem.objects.get_or_create(product=product, cart=self)

        if not created:
            li.quantity += quantity  # Update line item quantity.
        else:
            if quantity < 1000:  # Abort if quantity < 1000.
                li.delete()
                return

            li.quantity = quantity

        li.save()
        self.save()

    def update_line_item(self, product, quantity):
        """
        Update a line item from cart, update total price.
        Essentially accessed from cart view.
        """

        if quantity < 1000:  # Abort if quantity < 1000.
            return

        li, created = LineItem.objects.update_or_create(product=product, cart=self)

        li.quantity = quantity
        li.save()
        self.save()

    def remove_line_item(self, line_item):
        """Remove a line item from cart, update total price."""

        line_item.delete()
        self.save()

    def empty_cart(self):
        """Remove all line items from cart, reset total price to 0."""

        for li in self.lineitem_set.all():
            li.delete()

        self.save()

    def make_order(self):
        """
        Make order with line items of cart.
        We do not delete the line items,
        rather we create a new Order object,
        link the line items to it and then unlink them from the cart.

        returns : order[Order]
        """

        if self.total_price == 0:  # abort if cart is empty
            return

        order = Order.objects.create()
        order.add_comment()
        order.customer_account = self.customer_account

        for li in self.lineitem_set.all():
            li.order = order
            li.cart = None
            li.save()

        order.save()
        self.save()

        return order

    def save(self, *args, **kwargs):
        """We calculate the total price to populate / update the field."""

        self.calculate_total_price()

        return super().save(*args, **kwargs)


class Order(models.Model):
    """This is our order model."""

    class Meta:
        ordering = ["-date_created"]

    # Choices for the state :
    CREEE = "CR"
    EN_COURS_DE_TRAITEMENT = "CT"
    EN_ATTENTE_APPROVISIONNEMENT = "AA"
    PREPARATION_EXPEDITION = "PE"
    EN_ATTENTE_PAIEMENT = "AP"
    EXPEDIEE = "EX"
    TRAITEE_ARCHIVEE = "TA"
    ANNULEE = "AN"

    STATUS_CHOICES = [
        (CREEE, "Créée"),
        (EN_COURS_DE_TRAITEMENT, "En cours de traitement"),
        (EN_ATTENTE_APPROVISIONNEMENT, "En attente d'approvisionnement"),
        (PREPARATION_EXPEDITION, "En préparation à l'expédition"),
        (EN_ATTENTE_PAIEMENT, "En attente de paiement"),
        (EXPEDIEE, "Expédiée"),
        (TRAITEE_ARCHIVEE, "Traitée"),
        (ANNULEE, "Annulée"),
    ]

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=CREEE,
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incl_vat_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created = models.DateTimeField(default=timezone.now)
    ref_number = models.CharField(
        max_length=20, blank=True
    )  # generated in self.save() method.
    slug = models.SlugField(null=False, unique=True)
    customer_account = models.ForeignKey(
        CustomerAccount, on_delete=models.PROTECT, null=True
    )

    def __str__(self):
        return self.ref_number

    def calculate_total_price(self):
        """A utility method to summ up the prices of all the line items in order."""

        self.total_price = 0

        for li in LineItem.objects.filter(order=self):
            self.total_price += li.price

    def add_comment(self, content="La commande vient d'être créée."):
        """Add a new comment to order."""

        comment = Comment.objects.create(content=content, order=self)
        comment.save()

    def save(self, *args, **kwargs):
        """
        We get a random ref_number to populate the field,
        populate slug field,
        calculate the total price to populate the field,
        and finally populate vat_amount and incl_vat_price fields.
        """

        if not self.ref_number:
            self.ref_number = unique_ref_number_generator(self)

        if not self.slug:
            self.slug = slugify(self.ref_number)

        self.calculate_total_price()
        self.vat_amount, self.incl_vat_price = get_VAT_prices(self.total_price)

        return super().save(*args, **kwargs)


class Comment(models.Model):
    """This is our comment model, related to order model."""

    class Meta:
        ordering = ["-date_created"]

    content = models.CharField(max_length=2000, null=False)
    date_created = models.DateTimeField(default=timezone.now)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class LineItem(models.Model):
    """This is our line item model."""

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Model logic :
        Quantity must be >= 1000, if not we update it to 1000,
        we populate the price field when saving,
        (and the cart field as well ?)
        """

        if self.quantity < 1000:
            self.quantity = 1000

        self.price = self.product.price * self.quantity

        return super().save(*args, **kwargs)


class Conversation(models.Model):
    """This is our conversation model."""

    participants = models.ManyToManyField(User)
    subject = models.CharField(max_length=300)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.subject

    def add_message(self, author, content):
        """Add a message to conversation, update date_modified field."""

        Message.objects.create(author=author, content=content, conversation=self)
        self.date_modified = timezone.now()
        self.save()


class Message(models.Model):
    """This is our message model, related to conversation model."""

    class Meta:
        ordering = ["date_created"]

    author = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=5000, null=False)
    is_read = models.BooleanField(default=False, null=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=False)