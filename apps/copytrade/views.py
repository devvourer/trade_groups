from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import TradeGroup, Membership
from .serializers import TradeGroupSerializer, MembershipSerializer, TradeGroupCreateSerializer
from .tasks import withdraw_after_join_to_group, start_group, end_group
from .services import BinanceAPI

from apps.api.permissions import IsTrader, IsVerified, IsGroupOwner, WithdrawFromGroup
from apps.telegram_bot.tasks import notify_trader


class TraderGroupViewSet(RetrieveModelMixin,
                         ListModelMixin,
                         GenericViewSet):
    queryset = TradeGroup.objects.with_amount_collected().filter(status=TradeGroup.Status.RECRUITED).order_by('-created')
    serializer_class = TradeGroupSerializer
    permission_classes = [IsTrader, IsVerified]

    def get_serializer_class(self):
        if self.action == 'create':
            return TradeGroupCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'list':
            if not self.request.user.is_anonymous:
                return self.queryset.with_status_for_user(self.request.user)
        if self.action == 'retrieve':
            if not self.request.user.is_anonymous:
                return self.queryset.with_status_for_user(self.request.user).prefetch_related('memberships__investor')
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        start_group.apply_async((serializer.instance.id,), eta=serializer.instance.start_date)
        end_group.apply_async((serializer.instance.id,), eta=serializer.instance.end_date)
        data = serializer.data
        data['message'] = 'Группа создана'
        # action_trade_group.delay(serializer.instance.id)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post', 'get'], detail=False,
            serializer_class=MembershipSerializer,
            permission_classes=[IsAuthenticated])
    def join(self, request):
        if request.method == 'GET':
            serializer = MembershipSerializer()
            return Response(serializer.data)

        serializer = MembershipSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        withdraw_after_join_to_group.delay(serializer.instance.id)
        notify_trader.delay(serializer.instance.id)

        data = serializer.data
        data['message'] = 'Вы успешно присоединились'
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def leave_from_group(self, request, pk):
        instance = self.get_object()
        if instance.status == TradeGroup.Status.RECRUITED:
            try:
                membership = Membership.objects.get(investor=request.user, group=instance)
                user_balance = request.user.balance
                user_balance.balance += membership.invested_sum
                user_balance.save(update_fields=['balance'])
                membership.delete()
            except Exception as e:
                pass
            return Response({'message': 'Вы вышли из группы'}, status=status.HTTP_202_ACCEPTED)
        return Response({'message': 'Нельзя выйти из группы'}, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['post'], detail=True, permission_classes=[IsGroupOwner, WithdrawFromGroup])
    def withdraw(self, request, pk):
        """Вывод средств на binance"""
        binance_api = BinanceAPI()
        instance = self.get_object()
        return binance_api.withdraw_from_group(instance)

    @action(methods=['post'], detail=True, permission_classes=[IsGroupOwner])
    def delete(self, request, pk):
        instance = self.get_object()
        if instance.memberships.exists():
            return Response({'message': 'Нельзя удалить группу'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Группа удалена'}, status=status.HTTP_202_ACCEPTED)
