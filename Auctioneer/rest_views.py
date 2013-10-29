from django.http import HttpResponse
from rest_framework import serializers
from Auctioneer.models import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.contrib.auth import login, logout, authenticate
import base64


class AuctionsSerializer(serializers.ModelSerializer):

    seller = serializers.RelatedField(many=False, required=False)

    class Meta:
        model = Auctions
        fields = {'seller', 'title', 'description', 'startingPrice', 'startDate', 'stopDate'}


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def auctions(request):

    # Authenticate user
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].partition(' ')
        clear_text = base64.b64decode(auth[2])
        split = str(clear_text, 'UTF-8').partition(':')
        user = authenticate(username=split[0], password=split[2])

    if request.method == 'GET':
        data = JSONParser().parse(request)
        print(data)
        serializer = AuctionsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        else:
            return JSONResponse(serializer.errors, status=400)