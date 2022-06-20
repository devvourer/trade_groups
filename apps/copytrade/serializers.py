from rest_framework import serializers

from .models import TradeGroup, Membership
from apps.users.serializers import UserSerializer


class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Membership
        fields = ['id', 'invested_sum', 'date_joined', 'income']
        read_only_fields = ('investor', 'date_joined', 'income')

    def validate(self, attrs):
        group = TradeGroup.objects.get(id=attrs['id'])
        user = self.context['request'].user

        if user.is_trader:
            raise serializers.ValidationError({'message': 'Трейдеры не могут присоединятся к группам'})

        if attrs['invested_sum'] > user.balance.balance:
            raise serializers.ValidationError({'message': 'Не хватает баланса'})

        if Membership.objects.filter(
                investor=user.id,
                group=group
        ).exists():
            raise serializers.ValidationError({'message': 'Вы уже присоединились к этой группе'})

        if attrs['invested_sum'] < group.min_entry_sum:
            raise serializers.ValidationError({'message': 'Ошибка минимальной суммы входа'})

        elif attrs['invested_sum'] > group.max_entry_sum:
            raise serializers.ValidationError({'message': 'Ошибка максимальной суммы входа'})

        attrs['group'] = group
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['investor'] = self.context['request'].user
        return super().create(validated_data)


class MembershipListSerializer(serializers.ModelSerializer):
    investor = UserSerializer(required=False)

    class Meta:
        model = Membership
        fields = '__all__'


class TradeGroupSerializer(serializers.ModelSerializer):
    amount_collected = serializers.IntegerField(allow_null=True, required=False)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)
    status_for_user = serializers.BooleanField(required=False)
    memberships = MembershipListSerializer(required=False, many=True)

    class Meta:
        model = TradeGroup
        fields = '__all__'
        read_only_fields = ('trader', 'slug', 'created', 'id')


class TradeGroupCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TradeGroup
        fields = ('title', 'description', 'group_size',
                  'need_sum', 'percent_from_income',
                  'min_entry_sum', 'max_entry_sum',
                  'start_date', 'end_date')

    def validate(self, attrs):
        user = self.context['request'].user
        try:
            if user.trader:
                return super().validate(attrs)
        except:
            raise serializers.ValidationError({'message': 'Необходимо указать binance api ключи'})

    def create(self, validated_data):
        validated_data['trader'] = self.context['request'].user.trader
        return super().create(validated_data)
