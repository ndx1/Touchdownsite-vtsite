from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
    PasswordChangeDoneView,
)
from django.urls import path

from vtshop.message_views import MessageListView, ConversationListView
from vtshop.views import (
    AboutView,
    ContactFormView,
    HomeView,
    CustomerPasswordResetView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryListView,
    ProductDetailView,
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    CartView,
    CartEmptyView,
    ProductAddToCartView,
    LineItemRemoveFromCartView,
    LineItemUpdateView,
    OrderListView,
    OrderDetailView,
    MakeOrderView,
    UserSignInFormView,
    EmployeeCreateFormView,
    EmployeePwdUpdateView,
    EmployeeListView,
    MySpaceView,
    IntranetView,
    CustomerListView,
)

app_name = "vtshop"

urlpatterns = [
    ###################################
    ##### "STATIC" VIEWS W/O AUTH #####
    ###################################
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    ###################################
    ##### PRODUCTS AND CATEGORIES #####
    ###################################
    path("products/", ProductListView.as_view(), name="products-all"),
    path(
        "<slug:slug>/products/", ProductListView.as_view(), name="products"
    ),  # products filtered by category
    path(
        "<slug:slug>/product_detail/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path("product_form/", ProductCreateView.as_view(), name="product-create"),
    path("product_update_form/<slug:slug>/", ProductUpdateView.as_view(), name="product-update"),
    path("category_form/", CategoryCreateView.as_view(), name="category-create"),
    path("category_update_form/<slug:slug>/", CategoryUpdateView.as_view(), name="category-update"),
    path("categories/", CategoryListView.as_view(), name="categories"),
    ################
    ##### CART #####
    ################
    path("<int:pk>/cart/", CartView.as_view(), name="cart"),
    path("cart/", CartView.as_view(), name="cart"),
    ##### Redirect after cart update #####
    path(
        "product_add/<int:product_id>/",
        ProductAddToCartView.as_view(),
        name="product-add-to-cart",
    ),
    path(
        "line_item_update/<int:cart_id>/<int:line_item_id>/",
        LineItemUpdateView.as_view(),
        name="line-item-update",
    ),
    path(
        "line_item_remove/<int:line_item_id>/",
        LineItemRemoveFromCartView.as_view(),
        name="line-item-remove",
    ),
    path("<int:pk>/cart_empty/", CartEmptyView.as_view(), name="cart-empty"),
    path("<int:pk>/make_order/", MakeOrderView.as_view(), name="make-order"),
    ##################
    ##### ODRERS #####
    ##################
    path("orders/", OrderListView.as_view(), name="orders"),
    path("<slug:slug>/order_detail/", OrderDetailView.as_view(), name="order-detail"),
    ######################################
    ##### CONVERSATIONS AND MESSAGES #####
    ######################################
    #  all conversations, for employees for now.
    path("conversations/", ConversationListView.as_view(), name="conversations"),
    path("<int:pk>/messages/", MessageListView.as_view(), name="messages"),
    path(
        "<int:pk>/messages/<int:n_last>",
        MessageListView.as_view(),
        name="messages-last",
    ),
    #########################
    ##### ROLE SPECIFIC #####
    #########################
    ##### Administrator #####
    path("administration/employees/", EmployeeListView.as_view(), name="employees"),
    path(
        "administration/employee_create/",
        EmployeeCreateFormView.as_view(),
        name="employee_create",
    ),
    path(
        "administration/<int:pk>/employee_update/",
        EmployeePwdUpdateView.as_view(),
        name="employee_update",
    ),
    ##### EMPLOYEE #####
    path("intranet/", IntranetView.as_view(), name="intranet"),
    path("customers/", CustomerListView.as_view(), name="customers"),
    ##### CUSTOMER #####
    path("my_space/", MySpaceView.as_view(), name="my_space"),
    ##########################
    ##### AUTHENTICATION #####
    ##########################
    path(
        "login/",
        LoginView.as_view(
            template_name="vtshop/auth/login.html",
            # redirect_authenticated_user=True,
            next_page="/",
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(template_name="vtshop/auth/logout.html", next_page=None),
        name="logout",
    ),
    path("sign-in/", UserSignInFormView.as_view(), name="sign-in"),
    path(
        "password_reset/",
        CustomerPasswordResetView.as_view(
            template_name="vtshop/auth/password_reset_form.html",
            email_template_name="vtshop/auth/password_reset_email.html",
            success_url="/password_reset_done/",
        ),
        name="password_reset",
    ),
    # /password_reset_confirm_view
    path(
        "reset/<uidb64>/<token>",
        PasswordResetConfirmView.as_view(
            template_name="vtshop/auth/password_reset_confirm.html",
            success_url="/reset/done",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done",
        PasswordResetCompleteView.as_view(
            template_name="vtshop/auth/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
        "password_reset_done/",
        PasswordResetDoneView.as_view(
            template_name="vtshop/auth/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password_change_done/",
        PasswordChangeDoneView.as_view(
            template_name="vtshop/auth/password_change_done.html",
        ),
        name="password_change_done",
    ),
]