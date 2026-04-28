from django.db.models import Sum
from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer
from .models import Lead, Note


class NoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = (
            "id",
            "lead",
            "author",
            "author_name",
            "content",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "lead", "author", "created_at", "updated_at")

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else "Unknown"


class LeadSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    customer_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    notes = NoteSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_display = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "owner",
            "owner_name",
            "customer",
            "customer_id",
            "name",
            "email",
            "phone",
            "company",
            "status",
            "status_display",
            "source",
            "source_display",
            "value",
            "follow_up_date",
            "description",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def get_owner_name(self, obj):
        return obj.owner.full_name if obj.owner else ""

    def validate_customer_id(self, value):
        if value is None:
            return value

        customer = User.objects.filter(id=value, role=User.Role.CUSTOMER).first()
        if not customer:
            raise serializers.ValidationError("Selected customer is invalid.")
        return value

    def create(self, validated_data):
        customer_id = validated_data.pop("customer_id", None)
        if customer_id:
            validated_data["customer_id"] = customer_id
        return Lead.objects.create(**validated_data)

    def update(self, instance, validated_data):
        customer_id = validated_data.pop("customer_id", serializers.empty)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if customer_id is not serializers.empty:
            instance.customer_id = customer_id

        instance.save()
        return instance


class LeadListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_display = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "owner",
            "customer",
            "name",
            "email",
            "phone",
            "company",
            "status",
            "status_display",
            "source",
            "source_display",
            "value",
            "follow_up_date",
            "created_at",
            "updated_at",
        )


class DashboardSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())
    conversion_rate = serializers.FloatField()
    total_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    average_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    follow_ups = serializers.IntegerField()

    @staticmethod
    def build(queryset):
        total = queryset.count()
        closed = queryset.filter(status="closed").count()
        aggregates = queryset.aggregate(total_value=Sum("value"))
        total_value = aggregates["total_value"] or 0

        return {
            "total": total,
            "by_status": {
                "new": queryset.filter(status="new").count(),
                "contacted": queryset.filter(status="contacted").count(),
                "interested": queryset.filter(status="interested").count(),
                "closed": queryset.filter(status="closed").count(),
            },
            "conversion_rate": round((closed / total) * 100, 2) if total else 0,
            "total_value": total_value,
            "average_value": round(total_value / total, 2) if total else 0,
            "follow_ups": queryset.filter(follow_up_date__isnull=False).count(),
        }
