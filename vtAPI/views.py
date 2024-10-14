from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authentication import (
    TokenAuthentication,
)
from rest_framework.response import Response
from vtAPI.pemissions import IsEmployee

from vtshop.models import (
    CustomerAccount,
    Order,
    Comment,
    Product,
    Message,
    Conversation,
    LineItem,
)
from vtAPI.serializers import (
    UserSerializer,
    CustomerAccountSerializer,
    OrderSerializer,
    CommentSerializer,
    ConversationSerializer,
    MessageSerializer,
    ProductSerializer,
    LineItemSerializer,
    WholeOrderSerializer,
)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if "customer_account" in self.request.query_params:
            queryset = User.objects.filter(
                customeraccount=self.request.query_params["customer_account"]
            )
            return queryset

        elif "reg_number" in self.request.query_params:
            queryset = User.objects.filter(
                reg_number=self.request.query_params["reg_number"]
            )
            return queryset

        return super().get_queryset()


class CustomerAccountViewSet(viewsets.ModelViewSet):

    queryset = CustomerAccount.objects.all()
    serializer_class = CustomerAccountSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class UserRelatedOrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    # serializer_class = OrderSerializer
    serializer_class = WholeOrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role == "EMPLOYEE":
            queryset = Order.objects.all().filter(
                customer_account__employee_reg=user.reg_number
            )
        elif user.role == "CUSTOMER":
            queryset = Order.objects.all().filter(customer_account__customer=user)

        return queryset


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class ConversationViewSet(viewsets.ModelViewSet):

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class UserConversationViewSet(viewsets.ModelViewSet):

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        queryset = Conversation.objects.filter(participants=user).order_by(
            "date_modified"
        )

        return queryset


class MessageViewSet(viewsets.ModelViewSet):

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class LineItemViewSet(viewsets.ModelViewSet):

    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class WholeOrderViewListView(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = WholeOrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]