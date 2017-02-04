from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from kafka import KafkaProducer
import random
import redis 

from pybloom import BloomFilter
bloom_filter = BloomFilter(capacity=1000, error_rate=0.001)
try :
    with open("bloom","r") as bloom_file:
        bloom_filter = bloom_filter.fromfile(bloom_file)
except :
    print "File not found"
_redis = redis.StrictRedis(password='ShortenMe@)!&')
producer = KafkaProducer(bootstrap_servers='localhost:9092')

def validate_url(request):
    long_url = request.GET.get('long_url', None)
    data = {
        'is_taken': long_url == 'google.com'
    }
    return JsonResponse(data)

def manage_url(request, short_url):

    # check in bloom filter
    global bloom_filter
    try :
        with open("bloom","r") as bloom_file:
            bloom_filter = bloom_filter.fromfile(bloom_file)
    except :
        msg =  "File not found"
    
    if short_url not in bloom_filter: 
        msg = "your url not found - bloom filter" + ' bloom count ' + str(bloom_filter.count)
    else:
        # check in redis
        if _redis.exists(short_url):
            long_url = _redis.get(short_url)
            dailyhits = _redis.get('dailyhits:' + short_url)
            msg = "success"
        else:
            msg = "your url not found - redis"

    context = {
        'long_url' : long_url,
        'short_url' : short_url,
        'dailyhits' : dailyhits,
    } 

    return render(request, 'shorten_service/manage.html', context)
    

def redirect_url(request, short_url):
    status = 'error'
    # check in bloom filter
    global bloom_filter
    try :
        with open("bloom","r") as bloom_file:
            bloom_filter = bloom_filter.fromfile(bloom_file)
    except :
        print "File not found"
    
    if short_url not in bloom_filter: 
        response = "your url not found - bloom filter" + ' bloom count ' + str(bloom_filter.count)
    else:
        # check in redis
        if _redis.exists(short_url):
            status = 'success'
            long_url = _redis.get(short_url)
            response = "you are redirect to " + long_url
            # increase hit by 1 in redis - using namespace dailyhit:<short_url>
            _redis.set('dailyhits:' + short_url,int(_redis.get('dailyhits:' + short_url)) + 1)
        else:
            response = "your url not found - redis"
   
    if status == 'success':
        context = {
            'long_url' : long_url,
            'status' : status,
            'response' : response,
        }
        return render(request, 'shorten_service/redirect.html', context)

    return HttpResponse(response)

@csrf_exempt 
def encode_url(request):
    
    long_url = request.POST.get('long_url', None)
    # check long in redis
    if _redis.exists(long_url):
        short_url = _redis.get(long_url)
        data = {
                'short_url' : short_url,
               }
    else:
        short_url = generate_string()
        global bloom_filter

        # check if in bloom filter -> regenerate string
        while short_url in bloom_filter:
            short_url = generate_string()

        bloom_filter.add(str(short_url))
        
        with  open("bloom","w") as bloom_file:
            bloom_filter.tofile(bloom_file)

        # cache to redis - both way - long -> short, and short -> long
        _redis.set(long_url,short_url)
        _redis.set(short_url,long_url)
        # create dailyhits for short_url expire in 1 day
        _redis.set('dailyhits:' + short_url,0,86400)

        data = {
            'short_url': short_url,
            'exist' : short_url in bloom_filter
        }

        # publish a message to kafka topic url
        msg = str(short_url) +  ' ' + str(long_url)
        producer.send('url', b'%s' % msg)
    return JsonResponse(data)

def generate_string():
    num_char = 0
    string = ''
    _alphabet = '23456789bcdfghjkmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ-_'
    while ( num_char < 7 ):
        string += random.choice(_alphabet)
        num_char += 1
    return string

def index(request):
    return render(request, 'shorten_service/index.html')

def encode(request):
    pass
 
def results(request, url):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % url)
