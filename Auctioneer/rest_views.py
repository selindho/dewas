from django.http import HttpResponse
from rest_framework import serializers
from Auctioneer.models import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.contrib.auth import login, logout, authenticate
import base64
from django.views.decorators.csrf import csrf_exempt
from Auctioneer.views import bid_send_mail, bid_validate


class AuctionsSerializer(serializers.ModelSerializer):

    seller = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = Auctions
        fields = ('seller', 'title', 'description', 'startingPrice', 'startDate', 'stopDate')


class BidsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)


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
                return JSONResponse({"error": "no results"}, status=200)
        else:
            result = Auctions.get_by_query(query)
            if result is not None:
                serializer = AuctionsSerializer(result, many=True)
                return JSONResponse(serializer.data)
            else:
                return JSONResponse({"error": "no results"}, status=200)
    else:
        return JSONResponse({"error": "only method=get supported"}, status=200)


@csrf_exempt
def rest_bids(request, auction_id):

    auction = Auctions.get_by_id(auction_id)
    version = auction.version

    if request.method == 'POST':
        # Authenticate user
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].partition(' ')
            clear_text = base64.b64decode(auth[2])
            split = str(clear_text).partition(':')
            user = authenticate(username=split[0], password=split[2])
            if user is not None:
                try:
                    data = JSONParser().parse(request)
                except:
                    return JSONResponse({"error": "failed to parse request"}, status=200)

                serializer = BidsSerializer(data=data)
                if serializer.is_valid():

                    amount = str(serializer.object.get('amount'))
                    if auction is not None:
                        status = bid_validate(user, auction, version, amount)

                        if status == 'valid':
                            auction.version = int(auction.version) + 1
                            b = Bids(auction=auction, bidder=user, amount=amount, timestamp=datetime.now())
                            auction.save()
                            b.save()
                            bid_send_mail(user, auction)
                            return JSONResponse({"success": "bid placed"}, status=200)

                        else:
                            return JSONResponse({"error": status}, status=200)
                    else:
                        return JSONResponse({"error": "auction not found"}, status=200)

                else:
                    return JSONResponse({"error": "serialization failed"}, status=200)

            else:
                return JSONResponse({"error": "invalid credentials"}, status=200)

        else:
            return JSONResponse({"error": "authorization required"}, status=200)
    else:
        return JSONResponse({"error": "only method=post supported"}, status=200)