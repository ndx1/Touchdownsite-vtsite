from django.contrib.auth import get_user_model
from rest_framework import serializers

from vtshop.models import (
    Comment,
    Conversation,
    CustomerAccount,
    LineItem,
    Message,
    Order,
    Product,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    conversation_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    message_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    customer_account_set = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "reg_number",
            "role",
            "conversation_set",
            "message_set",
            "customer_account_set",
        ]
        read_only_fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "reg_number",
            "role",
            "conversation_set",
            "message_set",
            "customer_account_set",
        ]


class CustomerAccountSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source="customer.email")
    order_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = CustomerAccount
        fields = ["customer", "employee_reg", "order_set"]
        read_only_fields = ["employee_reg", "order_set"]


class CommentSerializer(serializers.ModelSerializer):
    order = serializers.ReadOnlyField(source="order.pk")
    order_id = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ["content", "order", "order_id"]


class OrderSerializer(serializers.ModelSerializer):
    customer_account = serializers.ReadOnlyField(source="customer_account.pk")
    lineitem_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comment_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "vat_amount",
            "incl_vat_price",
            "date_created",
            "ref_number",
            "slug",
            "customer_account",
            "lineitem_set",
            "comment_set",
        ]
        read_only_fields = [
            "id",
            "total_price",
            "vat_amount",
            "incl_vat_price",
            "date_created",
            "ref_number",
            "slug",
            "customer_account",
            "lineitem_set",
            "comment_set",
        ]


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.email")
    conversation = serializers.ReadOnlyField(source="conversation.id")
    conversation_id = serializers.IntegerField()
    class Meta:
        model = Message
        fields = [
            "id",
            "author",
            "date_created",
            "content",
            "is_read",
            "conversation",
            "conversation_id",
        ]
        read_only_fields = ["date_created"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    message_set = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = [
            "id",
            "subject",
            "date_created",
            "date_modified",
            "participants",
            "message_set",
        ]
        read_only_fields = ["subject", "date_created"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price"]
        read_only_fields = ["name", "price"]


class LineItemSerializer(serializers.ModelSerializer):
    product = serializers.ReadOnlyField(source="product.name")
    order = serializers.ReadOnlyField(source="order.id")

    class Meta:
        model = LineItem
        fields = ["product", "quantity", "price", "order"]
        read_only_fields = ["quantity", "price"]


class WholeOrderSerializer(OrderSerializer):
    lineitem_set = LineItemSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "vat_amount",
            "incl_vat_price",
            "date_created",
            "ref_number",
            "slug",
            "customer_account",
            "lineitem_set",
            "comment_set",
        ]
        read_only_fields = [
            "id",
            "total_price",
            "vat_amount",
            "incl_vat_price",
            "date_created",
            "ref_number",
            "slug",
            "customer_account",
            "lineitem_set",
            "comment_set",
        ]

