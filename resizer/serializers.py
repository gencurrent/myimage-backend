from rest_framework import serializers

class ResizeImageSerializer(serializers.Serializer):
    '''
    A class defining request properties for an image resizing
    '''
    width = serializers.IntegerField(required=True)
    height = serializers.IntegerField(required=True)
    # image_width = serializers.IntegerField(required=True)
    # image_height = serializers.IntegerField(required=True)