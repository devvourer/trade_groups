from rest_framework import serializers

from .models import PaymentOrder, PaymentOrderTether, Withdraw

from apps.users.utils import get_user_totp_device


class PaymentOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentOrder
        fields = ('amount', 'status', 'created')
        read_only_fields = ['status', 'created']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentOrderTetherSerializer(serializers.ModelSerializer):
    tx_id = serializers.CharField(allow_blank=True, max_length=260, required=False)

    class Meta:
        model = PaymentOrderTether
        fields = ('id', 'user', 'tx_id', 'created', 'amount', 'status')
        read_only_fields = ['created', 'amount', 'id', 'user', 'status']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WithdrawSerializer(serializers.ModelSerializer):
    two_fa_otp = serializers.CharField(allow_blank=True, required=False, max_length=6)

    class Meta:
        model = Withdraw
        fields = ('address', 'amount', 'created', 'status', 'two_fa_otp')
        read_only_fields = ['created', 'status']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        if user.otp_for_withdraw:
            device = get_user_totp_device(user)
            if device and device.confirmed:
                try:
                    code = attrs['two_fa_otp']
                    if not code:
                        raise serializers.ValidationError({
                            "message": "2fa_error"
                        })
                except KeyError as e:
                    raise serializers.ValidationError({"message": "Введите код Google authenticator"})
                if not device.verify_token(attrs['two_fa_otp']):
                    raise serializers.ValidationError({"message": "Ошибка кода Google authenticator"})
                attrs.pop('two_fa_otp')

        user_balance = user.balance
        if user_balance.balance < attrs.get('amount'):
            raise serializers.ValidationError({'message': 'Недостаточно баланса'})
        return super().validate(attrs)
