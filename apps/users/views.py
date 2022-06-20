from django.db.models import Prefetch
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.mixins import RetrieveModelMixin

from djoser.views import TokenCreateView

from apps.copytrade.serializers import MembershipSerializer, TradeGroupSerializer, MembershipListSerializer
from apps.copytrade.models import Membership, TradeGroup
from apps.payments.models import PaymentOrder, PaymentOrderTether, Withdraw
from apps.payments.serializers import WithdrawSerializer


from .models import User, Document, Trader, Banner, QA, Balance
from .serializers import TraderSerializer, DocumentSerializer,\
    TraderDashboardSerializer, BannerSerializer, OTPTokenCreateSerializer,\
    TOTPVerifyTokenSerializer, TOTPUpdateSerializer, UserSerializer, \
    FAQSerializer, UserProfileSerializer, UserChangePasswordSerializer,\
    UserPaymentsHistorySerializer, RatingSerializer, DocumentImageSerializer, BalanceSerializer
from .utils import get_user_totp_device


class TraderViewSet(GenericViewSet):
    model = Trader
    serializer_class = TraderSerializer
    queryset = Trader.objects.with_statistic()
    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=True,
            serializer_class=TraderDashboardSerializer,
            url_name='trader_info', permission_classes=[AllowAny])
    def trader_info(self, request, pk, **kwargs):
        instance = self.get_object()  # TODO: сделать запрос со статистикой
        serializer = TraderDashboardSerializer(instance)
        data = serializer.data
        data['rate'] = instance.get_rating()
        return Response(data)

    @action(methods=['get'], detail=False,
            serializer_class=TraderDashboardSerializer,)
    def dashboard(self, request):
        instance = self.queryset.get(user=request.user)
        serializer = TraderDashboardSerializer(instance)
        return Response(serializer.data)

    @action(methods=['get'], detail=False,
            serializer_class=TradeGroupSerializer)
    def groups(self, request):
        queryset = TradeGroup.objects.with_amount_collected().filter(trader=request.user.trader)
        serializer = TradeGroupSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, serializer_class=TradeGroupSerializer)
    def dashboard_groups(self, request, pk):
        queryset = TradeGroup.objects.with_amount_collected().filter(trader=pk)
        closed_groups = queryset.filter(status=TradeGroup.Status.COMPLETED)
        open_groups = queryset.filter(status=TradeGroup.Status.RECRUITED)
        serializer_open_groups = TradeGroupSerializer(open_groups, many=True)
        serializer_closed_groups = TradeGroupSerializer(closed_groups, many=True)

        return Response({'open': serializer_open_groups.data,
                         'closed': serializer_closed_groups.data},
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,
            serializer_class=TraderDashboardSerializer)
    def top_traders(self, request):
        serializer = TraderDashboardSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'],
            detail=False,
            url_name='trader_application',
            serializer_class=TraderSerializer)
    def apply_for_trader(self, request):
        """Подача заявки что-бы стать трейдером"""
        serializer = TraderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        request.user.is_trader = True
        request.user.save()
        return Response({'message': 'Вы успешно стали трейдером'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, serializer_class=RatingSerializer)
    def rate(self, request, pk):
        instance = self.get_object()
        serializer = RatingSerializer(data=request.data, context={'request': request, 'trader': instance})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Ваша оценка принята'}, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=True)
    def get_trades_history(self, request, pk):
        instance = self.get_object()
        data = instance.get_history_trades()
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_open_trades(self, request, pk):
        instance = self.get_object()
        data = instance.get_open_trades()
        return Response(data, status=status.HTTP_200_OK)


class BannerViewSet(GenericViewSet):
    model = Banner
    serializer_class = BannerSerializer
    queryset = Banner.objects.all()
    permission_classes = [AllowAny]

    @action(methods=['get'], detail=False, serializer_class=BannerSerializer)
    def get_banner(self, request):
        banner = self.queryset.last()
        serializer = BannerSerializer(banner)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 2fa
class OTPTokenCreateView(TokenCreateView):
    serializer_class = OTPTokenCreateSerializer


class TOTPViewSet(GenericViewSet):
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user = request.user
        device = get_user_totp_device(user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False)
        url = device.config_url
        return Response(url, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'patch'], serializer_class=TOTPUpdateSerializer, detail=False)
    def update_otp(self, request, *args, **kwargs):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        device = get_user_totp_device(request.user)
        if device and device.confirmed:
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.update(request.user, serializer.validated_data)
            data = serializer.data
            data['message'] = ' Успешно обновлено'
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response({"message": "Ошибка"}, status=status.HTTP_409_CONFLICT)

    @action(methods=['post'], serializer_class=TOTPVerifyTokenSerializer,
            detail=False)
    def verify(self, request):
        serializer = TOTPVerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        device = get_user_totp_device(user, confirmed=False)
        if not device:
            return Response({'message': 'Устройство не найдено'}, status=status.HTTP_404_NOT_FOUND)
        if device.verify_token(serializer.validated_data['token']):
            if not device.confirmed:
                device.confirmed = True
                device.save()
                user.otp_on()
            return Response(True, status=status.HTTP_200_OK)

        return Response({'message': 'Ошибка кода Google authenticator'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, serializer_class=TOTPVerifyTokenSerializer)
    def delete(self, request):
        serializer = TOTPVerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        device = get_user_totp_device(user)

        if device:
            if device.verify_token(serializer.validated_data['token']):
                user.otp_off()
                device.delete()
                return Response({'message': '2fa аутентификация отключена'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'message': 'Ошибка кода Google authenticator'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerificationView(GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(methods=['post', 'get'], detail=False)
    def verification(self, request):
        if request.method == "GET":
            try:
                document = Document.objects.filter(user=request.user).first()
                serializer = self.get_serializer(document)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(self.get_serializer(), status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        data['message'] = 'Заявка на верификацию принята'
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, serializer_class=DocumentImageSerializer)
    def upload_image(self, request):
        serializer = DocumentImageSerializer(data=request.data, many=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class InvestorDashboardView(GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.with_roi_level_and_profit().filter(is_active=True).select_related('balance')
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False)
    def dashboard(self, request):
        instance = self.queryset.get(id=request.user.id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, serializer_class=TradeGroupSerializer)
    def groups(self, request):
        # instance = self.queryset.get(id=request.user.id)
        queryset = TradeGroup.objects.filter(investors=request.user)\
            .with_amount_collected()\
            .with_status_for_user(request.user)
        serializer = TradeGroupSerializer(queryset, many=True)
        return Response(serializer.data)


class FAQView(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = FAQSerializer
    queryset = QA.objects.all()

    @action(methods=['get'], detail=False)
    def get(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


class UserProfileViewSet(GenericViewSet):
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    @action(methods=['get', 'patch'], detail=False, serializer_class=UserProfileSerializer)
    def profile(self, request):
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        self.perform_update(serializer)
        return Response({'message': 'Профиль успешно обновлен'}, status=status.HTTP_202_ACCEPTED)

    @action(methods=['get', 'patch'], detail=False, serializer_class=UserChangePasswordSerializer)
    def change_password(self, request):
        if request.method == 'GET':
            serializer = UserChangePasswordSerializer()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserChangePasswordSerializer(request.user, data=request.data, partial=True, context={'request': request})
        self.perform_update(serializer)
        return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def perform_update(serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()


class PaymentsHistoryViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        status = self.request.query_params.get('status')

        if self.action == "payments":
            queryset = User.objects.filter(id=self.request.user.id)
            if start_date and end_date and status:
                return queryset.prefetch_related(
                    Prefetch('payments', queryset=PaymentOrder.objects.filter(
                        created__date__range=(start_date, end_date), status=status
                    )),
                    Prefetch('tether_payments', queryset=PaymentOrderTether.objects.filter(
                        created__date__range=(start_date, end_date), status=status)
                             )
                )
            elif start_date and end_date:
                return queryset.prefetch_related(
                    Prefetch('payments', queryset=PaymentOrder.objects.filter(
                        created__date__range=(start_date, end_date))),
                    Prefetch('tether_payments', queryset=PaymentOrderTether.objects.filter(
                        created__date__range=(start_date, end_date)))
                )
            return queryset.prefetch_related('payments', 'tether_payments')
        if self.action == 'withdraws':
            queryset = Withdraw.objects.filter(user=self.request.user)
            if status:
                queryset = queryset.filter(status=status)
            if start_date and end_date:
                return queryset.filter(created__date__range=(start_date, end_date))
            return queryset

        if self.action == 'join_to_groups':
            queryset = Membership.objects.filter(investor=self.request.user).prefetch_related('group')
            if start_date and end_date:
                return queryset.filter(date_joined__date__range=(start_date, end_date))
            return queryset

        if self.action == 'income_from_groups':
            queryset = Membership.objects.filter(investor=self.request.user, income__gte=0).prefetch_related('group')
            if start_date and end_date:
                return queryset.filter(date_joined__date__range=(start_date, end_date))
            return queryset

    def get_serializer_class(self):
        if self.action == 'payments':
            return UserPaymentsHistorySerializer
        if self.action == 'withdraws':
            return WithdrawSerializer
        if self.action == 'join_to_groups':
            return MembershipSerializer
        if self.action == 'income_from_groups':
            return MembershipSerializer

    @action(methods=['get'], detail=False)
    def payments(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def withdraws(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def join_to_groups(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def income_from_groups(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BalanceViewSet(GenericViewSet):
    serializer_class = BalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)

    @action(methods=['get'], detail=False)
    def balance(self, request):
        queryset = self.get_queryset().first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


