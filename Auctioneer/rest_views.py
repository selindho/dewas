from django.http import HttpResponse
from rest_framework import serializers
from Auctioneer.models import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.contrib.auth import login, logout, authenticate
import base64
from django.views.decorators.csrf import csrf_exempt


class AuctionsSerializer(serializers.ModelSerializer):

    seller = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = Auctions
        fields = ('seller', 'title', 'description', 'startingPrice', 'startDate', 'stopDate')


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def rest_auctions(request, query):

    if request.method == 'GET':
        if query is None:
            result = Auctions.get_all()
            if result is not None:
                serializer = AuctionsSerializer(result, many=True)
                return JSONResponse(serializer.data)
            else:
                return JSONResponse({'error': 'no results'}, status=200)
        else:
            result = Auctions.get_by_query(query)
            if result is not None:
                serializer = AuctionsSerializer(result, many=True)
                return JSONResponse(serializer.data)
            else:
                return JSONResponse({'error': 'no results'}, status=200)


def rest_bids(request):

    if request.method == 'POST':
        # Authenticate user
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].partition(' ')
            clear_text = base64.b64decode(auth[2])
            split = str(clear_text, 'UTF-8').partition(':')
            user = authenticate(username=split[0], password=split[2])