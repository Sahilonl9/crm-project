from rest_framework import serializers
from .models import Lead, Note


class NoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ('id', 'lead', 'author', 'author_name', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else 'Unknown'


class LeadSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = Lead
        fields = (
            'id', 'owner', 'owner_name',
            'name', 'email', 'phone', 'company',
            'status', 'status_display',
            'source', 'source_display',
            'value', 'follow_up_date', 'description',
            'notes', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    def get_owner_name(self, obj):
        return obj.owner.full_name if obj.owner else ''


class LeadListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views (no nested notes)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = Lead
        fields = (
            'id', 'name', 'email', 'phone', 'company',
            'status', 'status_display',
            'source', 'source_display',
            'value', 'follow_up_date',
            'created_at', 'updated_at',
        )


class DashboardSerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())
    conversion_rate = serializers.FloatField()
    total_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    won_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    follow_ups_today = serializers.IntegerField()
    recent_leads = LeadListSerializer(many=True)