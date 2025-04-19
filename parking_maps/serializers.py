from rest_framework import serializers
from .models import ParkingMap


class ParkingMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingMap
        fields = ['id', 'name', 'svg_file', 'description', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['uploaded_at', 'uploaded_by']

    def validate_svg_file(self, file):
        """
        Проверка, что загружаемый файл является SVG.
        """
        if not file.name.endswith('.svg'):
            raise serializers.ValidationError("Файл должен иметь расширение .svg")
        return file

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
