from rest_framework import serializers

class CropImageSerializer(serializers.Serializer):
    '''
    A class defining request properties for an image cropping
    '''
    x = serializers.FloatField(required=True)
    y = serializers.FloatField(required=True)
    width = serializers.FloatField(required=True)
    height = serializers.FloatField(required=True)
    image_width = serializers.IntegerField(required=True)
    image_height = serializers.IntegerField(required=True)
    