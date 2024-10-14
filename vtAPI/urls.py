"""Our urls for the API."""

from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views as authviews
# from rest_framework_simplejwt.views import (
#                                             TokenObtainPairView,
#                                             TokenRefreshView,
#                                             )
from vtAPI import views, auth_token

app_name = "vtAPI"

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'customeraccounts', views.CustomerAccountViewSet)
router.register(r'orders', views.OrderViewSet, basename="order")
router.register(r'whole_orders', views.WholeOrderViewListView, basename="whole_order")
router.register(r'user_orders', views.UserRelatedOrderViewSet, basename="user_order")
router.register(r'comments', views.CommentViewSet)
router.register(r'user_conversations', views.UserConversationViewSet)
router.register(r'conversations', views.ConversationViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'lineitems', views.LineItemViewSet)

urlpatterns = [
    path('', include(router.urls,)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('api-token-auth/', authviews.obtain_auth_token),
    path('api-token-auth/', auth_token.CustomAuthToken.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]