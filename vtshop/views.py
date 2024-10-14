from django.shortcuts import render

# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    RedirectView,
    FormView,
)
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.db import IntegrityError

from vtshop.models import (
    Category,
    Product,
    Cart,
    LineItem,
    Order,
    User,
    Conversation,
)
from vtshop.forms import ContactForm, UserForm, EmployeePwdUpdateForm
from vtshop.auth_utils import (
    TestIsCustomerMixin,
    TestIsEmployeeMixin,
    TestIsAdministratorMixin,
)


class HomeView(TemplateView):
    template_name = "vtshop/home.html"


class AboutView(TemplateView):
    template_name = "vtshop/about.html"


class ContactFormView(FormView):
    """Our contact page form view."""

    template_name = "vtshop/contact.html"
    form_class = ContactForm
    success_url = "/"

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super().form_valid(form)


#########################
##### USER SPECIFIC #####
#########################


class CustomerPasswordResetView(PasswordResetView):
    """Our Customer Reset password class."""

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = (form.cleaned_data["email"],)
            # print("cleaned_email : ", email)
            user = User.objects.filter(email=email[0])
            # test = User.objects.all()
            # for t in test:
            #     print(t, "email = ", t.email)

            if user.count() > 0:
                # print(user)
                # Password change available only to registrated Customers.
                if user[0].role == "CUSTOMER":
                    return super().post(request, *args, **kwargs)
            else:
                # Redirect here anyway to avoid leaking info about registered emails.
                return HttpResponseRedirect(reverse("vtshop:password_reset_done"))


class UserSignInFormView(FormView):
    """Our user sing in view."""

    template_name = "vtshop/auth/sign-in.html"
    form_class = UserForm
    success_url = "/login"

    def form_valid(self, form):
        """Process to create a new "customer"."""

        form.create_user(role="CUSTOMER")
        return super().form_valid(form)


class EmployeeCreateFormView(LoginRequiredMixin, TestIsAdministratorMixin, FormView):
    """Our employee creation form view, for administrator."""

    login_url = "/login/"
    form_class = UserForm
    template_name = "vtshop/administration/employee_form.html"
    success_url = "/administration/employees"

    def form_valid(self, form):
        """Process to create a new "employee"."""

        form.create_user(role="EMPLOYEE")
        return super().form_valid(form)


class EmployeePwdUpdateView(LoginRequiredMixin, TestIsAdministratorMixin, FormView):
    """
    Our employee password update view, for administrator.
    """

    login_url = "/login/"
    form_class = EmployeePwdUpdateForm
    template_name = "vtshop/administration/employee_update_form.html"
    success_url = "/administration/employees"

    def form_valid(self, form):
        """Process to update employee's password."""

        # !!!! password_validation.validate_password ???!!!
        # For all forms !!!!

        form.update_employee_pwd(user_id=self.kwargs["pk"])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Employee details and old password to be displayed."""

        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(User, pk=self.kwargs["pk"])

        context["employee"] = employee
        return context


class EmployeeListView(LoginRequiredMixin, TestIsAdministratorMixin, ListView):
    """Our employee list view."""

    login_url = "/login/"
    model = User
    template_name = "vtshop/administration/employees.html"
    context_object_name = "employee_list"

    def get_queryset(self):
        """Get employee list."""

        employee_list = User.objects.filter(role="EMPLOYEE").order_by("date_joined")
        return employee_list


class MySpaceView(LoginRequiredMixin, TestIsCustomerMixin, ListView):
    """Main view for customer's "my space"."""

    login_url = "/login/"
    template_name = "vtshop/customer/my_space.html"
    model = Order
    paginate_by = 100  # if pagination is desired
    context_object_name = "order_list"

    def get_queryset(self):
        """
        Return all orders (ordered in model by date_created),
        for an owner (aka CustomerAccount)
        """
        return Order.objects.filter(customer_account=self.request.user.customeraccount)

    def get_context_data(self, **kwargs):
        """Get related employee and conversation"""

        context = super().get_context_data(**kwargs)
        user = self.request.user

        related_employee = get_object_or_404(
            User, reg_number=user.customeraccount.employee_reg
        )
        context["related_employee"] = related_employee

        # context["conversation"] = get_object_or_404(Conversation, customer_account=user.customeraccount)
        context["conversation"] = Conversation.objects.filter(participants=user).filter(
            participants=related_employee
        )[0]

        return context


class IntranetView(LoginRequiredMixin, TestIsEmployeeMixin, TemplateView):
    """Main view for employee's Intranet."""

    login_url = "/login/"
    template_name = "vtshop/employee/intranet.html"


class CustomerListView(LoginRequiredMixin, TestIsEmployeeMixin, ListView):
    """Employee's related customer list view."""

    login_url = "/login/"
    model = User
    template_name = "vtshop/employee/customers.html"
    context_object_name = "customer_list"

    def get_queryset(self):
        """Get employee's related customer list."""

        user = self.request.user
        customer_list = User.objects.filter(
            role="CUSTOMER", customeraccount__employee_reg=user.reg_number
        ).order_by("date_joined")

        return customer_list


###################################
##### PRODUCTS AND CATEGORIES #####
###################################


class ProductCreateView(LoginRequiredMixin, TestIsEmployeeMixin, CreateView):
    """Our view to create a new product."""

    login_url = "/login/"
    model = Product
    fields = ["name", "image", "description", "price", "category"]
    success_url = "/products/"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except IntegrityError as err:
            return render(
                self.request,
                "vtshop/product_form.html",
                {
                    "error_message": "Le Libellé est trop similaire à un produit existant, veuillez le changer svp.",
                    "form": form,
                },
            )
        return response


class ProductUpdateView(LoginRequiredMixin, TestIsEmployeeMixin, UpdateView):
    """Our view to update an existing product."""
    
    login_url = "/login/"
    model = Product
    fields = ["name", "image", "description", "price", "category"]
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except IntegrityError as err:
            return render(
                self.request,
                "vtshop/product_form.html",
                {
                    "error_message": "Le Libellé est trop similaire à un produit existant, veuillez le changer svp.",
                    "form": form,
                },
            )
        return response
    

class ProductView(TemplateView):
    """Our product view."""

    template_name = "vtshop/products.html"

    def get_queryset(self):
        """
        Return all categories ordered by name.
        """
        return Category.objects.all().order_by("name")


class ProductListView(ListView):
    """Our product-by-category list view."""

    model = Product
    # paginate_by = 100  # if pagination is desired
    template_name = "vtshop/products.html"
    context_object_name = "product_list"

    def get_queryset(self, **kwargs):
        """
        Return products by category, ordered by creation date, and with price multiplied by 1000.
        """

        if "slug" in self.kwargs:
            p_set = Product.objects.filter(category__slug=self.kwargs["slug"]).order_by(
                "name"
            )
        else:
            p_set = Product.objects.all().order_by("name")

        for product in p_set:
            product.price *= 1000

        return p_set

    def get_context_data(self, **kwargs):
        """
        We want the actual category if specified,
        and the list of all categories to build our filter.
        """

        context = super().get_context_data(**kwargs)

        if "slug" in self.kwargs:
            actual_category = Category.objects.filter(slug=self.kwargs["slug"])
            if actual_category.exists():
                context["actual_category"] = actual_category[0]

        context["category_list"] = Category.objects.all().order_by("name")

        return context


class ProductDetailView(DetailView):
    """Our product's detailed view."""

    model = Product
    template_name = "vtshop/product_detail.html"


class CategoryCreateView(LoginRequiredMixin, TestIsEmployeeMixin, CreateView):
    """Our view to create a new category."""

    login_url = "/login/"
    model = Category
    fields = ["name"]
    success_url = "/products/"

    def form_valid(self, form):
        try:
            # Check if name is not "api" which would cause url routing problems.
            if form.cleaned_data["name"] == "api":
                raise IntegrityError()
            response = super().form_valid(form)
        except IntegrityError as err:
            return render(
                self.request,
                "vtshop/category_form.html",
                {
                    "error_message": "Le nom est trop similaire à une catégorie existante, veuillez le modifier svp.",
                    "form": form,
                },
            )
        return response


class CategoryUpdateView(LoginRequiredMixin, TestIsEmployeeMixin, UpdateView):
    """Our view to update a category name."""

    login_url = "/login/"
    model = Category
    fields = ["name"]
    template_name_suffix = "_update_form"
    success_url = "/categories/"

    def form_valid(self, form):
        try:
            # Check if name is not "api" which would cause url routing problems.
            if form.cleaned_data["name"] == "api":
                raise IntegrityError()
            response = super().form_valid(form)
        except IntegrityError as err:
            return render(
                self.request,
                "vtshop/category_form.html",
                {
                    "error_message": "Le nom est trop similaire à une catégorie existante, veuillez le modifier svp.",
                    "form": form,
                },
            )

        return response


class CategoryListView(ListView):
    """Our category list view."""

    model = Category
    # paginate_by = 100  # if pagination is desired
    template_name = "vtshop/categories.html"
    context_object_name = "category_list"


################
##### CART #####
################


class CartView(LoginRequiredMixin, TestIsCustomerMixin, TemplateView):
    """The owner's cart view."""

    login_url = "/login/"
    template_name = "vtshop/cart.html"

    def get_context_data(self, **kwargs):
        """Cart with line item list to be displayed."""

        context = super().get_context_data(**kwargs)
        cart = get_object_or_404(
            Cart, customer_account=self.request.user.customeraccount
        )

        context["cart"] = cart
        context["line_item_list"] = cart.lineitem_set.all().order_by("product")
        return context


class ProductAddToCartView(LoginRequiredMixin, TestIsCustomerMixin, RedirectView):
    """Add a product (aka a line item) to cart"""

    login_url = "/login/"
    http_method_names = ["post"]
    pattern_name = "vtshop:product-detail"

    def get_redirect_url(self, *args, **kwargs):
        """Add product to cart and redirect"""

        # cart = get_object_or_404(Cart, pk=kwargs["cart_id"])
        cart = get_object_or_404(
            Cart, customer_account=self.request.user.customeraccount
        )
        product = get_object_or_404(Product, pk=kwargs["product_id"])
        cart.add_line_item(product, 1000)

        kwargs = {}
        args = (product.slug,)
        return super().get_redirect_url(*args, **kwargs)


class LineItemUpdateView(LoginRequiredMixin, TestIsCustomerMixin, RedirectView):
    """Update a line item quantity in cart"""

    login_url = "/login/"
    http_method_names = ["post"]
    pattern_name = "vtshop:cart"

    def post(self, request, *args, **kwargs):
        """update quantity, checking its value"""

        if "quantity" in request.POST:
            try:
                quantity = int(request.POST["quantity"])
            except:
                quantity = 1000

            if quantity >= 1000:
                cart = get_object_or_404(Cart, pk=kwargs["cart_id"])
                line_item = get_object_or_404(LineItem, pk=kwargs["line_item_id"])
                cart.update_line_item(line_item.product, quantity)

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        """Redirect to cart view."""

        # return super().get_redirect_url(*args, kwargs["cart_id"])
        args = (kwargs["cart_id"],)
        kwargs = {}
        return super().get_redirect_url(*args, **kwargs)


class LineItemRemoveFromCartView(LoginRequiredMixin, TestIsCustomerMixin, RedirectView):
    """Remove a line item (aka a product) from cart"""

    login_url = "/login/"
    http_method_names = ["post"]
    pattern_name = "vtshop:cart"

    def get_redirect_url(self, *args, **kwargs):
        """Delete line item and redirect to cart view"""

        line_item = get_object_or_404(LineItem, pk=kwargs["line_item_id"])
        cart = line_item.cart
        line_item.delete()
        cart.save()

        kwargs = {}
        kwargs["cart_id"] = cart.id
        return super().get_redirect_url(*args, kwargs["cart_id"])


class CartEmptyView(LoginRequiredMixin, TestIsCustomerMixin, RedirectView):
    """Remove all line items (aka products) from cart"""

    login_url = "/login/"
    http_method_names = ["post"]
    pattern_name = "vtshop:cart"

    def get_redirect_url(self, *args, **kwargs):
        """Empty cart"""

        cart = get_object_or_404(Cart, pk=kwargs["pk"])
        cart.empty_cart()

        kwargs = {}
        return super().get_redirect_url(*args, **kwargs)


#################
##### ORDER #####
#################


class MakeOrderView(LoginRequiredMixin, TestIsCustomerMixin, RedirectView):
    """Make order from cart."""

    login_url = "/login/"
    http_method_names = ["post"]
    pattern_name = "vtshop:order-detail"

    def get_redirect_url(self, *args, **kwargs):
        """Make order."""

        cart = get_object_or_404(Cart, pk=kwargs["pk"])
        order = cart.make_order()

        kwargs = {}
        args = (order.slug,)
        return super().get_redirect_url(*args, **kwargs)


class OrderListView(LoginRequiredMixin, TestIsCustomerMixin, ListView):
    """Our order list view."""

    login_url = "/login/"
    model = Order
    paginate_by = 100  # if pagination is desired
    template_name = "vtshop/orders.html"
    context_object_name = "order_list"

    def get_queryset(self):
        """
        Return all orders (ordered in model by date_created),
        for an owner (aka CustomerAccount)
        """
        return Order.objects.all()


class OrderDetailView(LoginRequiredMixin, TestIsCustomerMixin, DetailView):
    """Our order's detailed view."""

    login_url = "/login/"
    model = Order
    template_name = "vtshop/order_detail.html"

    def get_context_data(self, **kwargs):
        """Line item list, order status and last comment to be displayed."""

        context = super().get_context_data(**kwargs)
        order = self.get_object()

        context["line_item_list"] = order.lineitem_set.all()

        comments = order.comment_set.all()
        if comments.count() > 0:
            context["comment"] = comments[0]
        else:
            context["comment"] = False

        status_tuple_list = [st for st in Order.STATUS_CHOICES if st[0] == order.status]
        context["status"] = status_tuple_list[0][1]

        return context