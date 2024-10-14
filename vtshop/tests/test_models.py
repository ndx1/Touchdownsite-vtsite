from decimal import Decimal

from django.test import TestCase

from vtshop.models import (User, Product, LineItem, 
                            Cart, Order, Comment, 
                            Conversation, Message, 
                            CustomerAccount)
from vtshop.tests.utils_tests import create_employee1, create_customer1

class OrderTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.order = Order.objects.create()

    def test_add_comment(self):
        # Arrange.
        com_count = Comment.objects.all().count()

        # Act.
        self.order.add_comment("test")
        order_comments = self.order.comment_set.all()

        # Assert.
        self.assertEqual(com_count + 1, Comment.objects.all().count())
        self.assertEqual(list(order_comments)[0].content, "test")


class CommentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:

        cls.order = Order.objects.create()

    def test_message_ordering_in_queryset(self):
        
        # Arrange.
        self.order.add_comment("test1")
        self.order.add_comment("test2")
        self.order.add_comment("test3")

        # Act.
        order_comments = self.order.comment_set.all()

        # Assert.
        self.assertTrue(
            order_comments[0].date_created > 
            order_comments[1].date_created > 
            order_comments[2].date_created
        )


class CartTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:

        cls.product1 = Product.objects.create(
            name="product1", 
            description="description1",
            price=4242, 
        )

        cls.product2 = Product.objects.create(
            name="product2", 
            description="description1",
            price=6789, 
        )

        cls.cart = Cart.objects.create()

    def test_initial_total_price_is_0(self):

        # Assert.
        self.assertEqual(self.cart.total_price, 0)
        
    def test_add_line_item(self):

        # Arrange.
        li_set_count = LineItem.objects.filter(cart=self.cart).count()

        # Act.
        self.cart.add_line_item(self.product1, 1234)
        li_set = self.cart.lineitem_set.all()

        # Assert.
        self.assertEqual(li_set_count + 1, LineItem.objects.filter(cart=self.cart).count())
        self.assertEqual(self.cart.total_price, self.product1.price * 1234)

    def test_add_line_item_quantity_less_than_1000(self):

        # Arrange.
        li_set_count = LineItem.objects.filter(cart=self.cart).count()

        # Act.
        self.cart.add_line_item(self.product1, 123)

        # Assert.
        self.assertEqual(li_set_count , LineItem.objects.filter(cart=self.cart).count())
        self.assertEqual(self.cart.total_price, 0)
    
    def test_add_same_product_twice_to_cart(self):

        # Arrange.
        li_set_count = LineItem.objects.filter(cart=self.cart).count()

        # Act.
        self.cart.add_line_item(self.product1, 1234)
        self.cart.add_line_item(self.product1, 123)

        # Assert.
        self.assertEqual(li_set_count + 1, LineItem.objects.filter(cart=self.cart).count())
        self.assertEqual(self.cart.total_price, self.product1.price * (1234 + 123))

    def test_update_line_item(self):

        # Act.
        self.cart.add_line_item(self.product1, 1234)
        self.cart.update_line_item(self.product1, 5678)

        # Assert.
        self.assertEqual(self.cart.total_price, self.product1.price * 5678)
    
    def test_update_line_item_quantity_less_than_1000(self):

        # Act.
        self.cart.add_line_item(self.product1, 1234)
        self.cart.update_line_item(self.product1, 123)

        # Assert.
        self.assertEqual(self.cart.total_price, self.product1.price * 1234)

    def test_remove_line_item(self):

        # Arrange.
        self.cart.add_line_item(self.product1, 1234)

        li_set = LineItem.objects.filter(cart=self.cart)
        li_set_count = li_set.count()

        # Act.
        self.cart.remove_line_item(li_set[0])

        # Assert.
        self.assertEqual(self.cart.total_price, 0)
        self.assertEqual(LineItem.objects.filter(cart=self.cart).count(), li_set_count - 1)

    def test_empty_cart(self):

        # Arrange.
        self.cart.add_line_item(self.product1, 1234)
        self.cart.add_line_item(self.product2, 5678)

        # Act.
        self.cart.empty_cart()

        # Assert.
        self.assertEqual(self.cart.total_price, 0)
        self.assertEqual(LineItem.objects.filter(cart=self.cart).count(), 0)

    def test_calculate_total_price(self):

        # Arrange.
        self.cart.add_line_item(self.product1, 1234)
        self.cart.add_line_item(self.product2, 5678)

        # Act.
        self.cart.calculate_total_price()

        # Assert.
        self.assertEqual(self.cart.total_price, 4242 * 1234 + 6789 * 5678)

    def test_make_order_aborted_if_empty_cart(self):

        o_count = Order.objects.all().count()

        # Act.
        self.cart.make_order()

        # Assert.
        self.assertEqual(Order.objects.all().count(), o_count)

    def test_make_order_cart_emptied(self):

        # Arrange.
        self.cart.add_line_item(self.product1, 1234)
        o_count = Order.objects.all().count()

        # Act.
        self.cart.make_order()

        # Assert.
        self.assertEqual(Order.objects.all().count(), o_count + 1)
        self.assertEqual(self.cart.lineitem_set.all().count(), 0)
        self.assertEqual(self.cart.total_price, 0)
    
    def test_make_order_check_order_is_correctly_populated(self):

        # Arrange.
        self.cart.add_line_item(self.product1, 1234)
        self.cart.add_line_item(self.product2, 5678)
        cart_tp = self.cart.total_price
        li_list = list(self.cart.lineitem_set.all())

        # Act.
        self.cart.make_order()
        
        # Assert.
        o_set = Order.objects.all()
        order = o_set[o_set.count() - 1]

        self.assertListEqual(list(order.lineitem_set.all()), li_list)
        self.assertEqual(order.total_price, cart_tp)

    def test_make_order(self):

        # Arrange.
        self.cart.add_line_item(self.product1, 1000)
        self.cart.add_line_item(self.product2, 1000)
        cart_total_price = self.cart.total_price
        line_item_set = self.cart.lineitem_set.all()

        # Act.
        order = self.cart.make_order()

        # Assert.
        self.assertEqual(self.cart.lineitem_set.all().count(), 0)
        self.assertEqual(self.cart.total_price, 0)
        self.assertEqual(order.total_price, cart_total_price)
        for li in range(0, line_item_set.count()):
            li_pk = li.pk
            self.assertIn(LineItem.objects.filter(pk=li_pk), order.lineitem_set.all())

    def test_make_order_assigns_new_order_to_customer_account(self):

        # Arrange.
        ca = CustomerAccount.objects.create()
        ca.set_cart()
        cart = ca.cart
        cart.add_line_item(self.product1, 1000)
        assigned_order_count = Order.objects.filter(customer_account = ca).count()

        # Act.
        cart.make_order()

        # Assert.
        self.assertEqual(assigned_order_count + 1, Order.objects.filter(customer_account = ca).count())


class LineItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Arrange."""

        cls.product1 = Product.objects.create(
            name="product1", 
            description="description1",
            price=4242, 
        )

    def test_line_item_quantity_ge_1000(self):

        # Act.
        li = LineItem.objects.create(product=self.product1, quantity=900)

        # Assert.
        self.assertEqual(li.quantity, 1000)

    def test_line_item_price_create(self):

        # Act.
        li = LineItem.objects.create(product=self.product1, quantity=1000)

        # Assert.
        self.assertEqual(self.product1.price * 1000, li.price)


class ConversationTestCase(TestCase):

    def test_add_message(self):

        # Arrange.
        conversation = Conversation.objects.create(subject="test")
        message_content = "This is a test."
        # message_author = "Hi test."
        message_author = create_customer1()

        # Act.
        message_count = Message.objects.all().count()
        # conversation.add_message(author=message_author, content=message_content)
        conversation.add_message(author=message_author, content=message_content)
        message = conversation.message_set.all()[0]

        # Assert.
        self.assertEqual(message_count + 1, Message.objects.all().count())
        self.assertEqual(message.author, message_author)
        self.assertEqual(message.content, message_content)


class CustomerAccountTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.cart_count = Cart.objects.all().count()
        cls.conversation_count = Conversation.objects.all().count()
        cls.ca = CustomerAccount.objects.create()
        cls.customer = User.objects.create(
            email = "customer1@test.com",
            password = "12345678&",
            first_name = "cust1_first_name",
            last_name = "cust1_last_name",
        )

    def test_set_cart(self):

        # Act.
        self.ca.set_cart()

        # Assert.
        self.assertEqual(self.cart_count + 1, Cart.objects.all().count())
        self.assertEqual(self.ca.cart.customer_account.pk, self.ca.pk)
    
    def test_set_cart_called_twice_does_not_create_second_cart(self):

        # Act.
        self.ca.set_cart()
        self.ca.set_cart()

        # Assert.
        self.assertEqual(self.cart_count + 1, Cart.objects.all().count())
        self.assertEqual(self.ca.cart.customer_account.pk, self.ca.pk)
    
    def test_set_conversation(self):

        # Act.
        self.ca.set_conversation("test", self.customer)

        # Assert.
        self.assertEqual(self.conversation_count + 1, Conversation.objects.all().count())
    
    def test_set_conversation_called_twice_does_not_create_second_conversation(self):

        # Act.
        self.ca.set_conversation("test", self.customer)
        self.ca.set_conversation("test", self.customer)

        # Assert.
        self.assertEqual(self.conversation_count + 1, Conversation.objects.all().count())