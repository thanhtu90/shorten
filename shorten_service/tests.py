from django.test import TestCase

# Create your tests here.

# test kafka-python
from kafka import KafkaProducer

print 'test kafka-python'
producer = KafkaProducer(bootstrap_servers='localhost:9092')
for _ in range(10):
     producer.send('url', b'some_message_bytes')

# test bloom filter
from pybloom import BloomFilter
print bloom_filter
print "test bloom filter"
f = BloomFilter(capacity=1000, error_rate=0.001)

[f.add(x) for x in range(10)]
print all([(x in f) for x in range(10)])
print 10 in f
print 5 in f

print "\ntest redis"
import redis
r = redis.StrictRedis(password='ShortenMe@)!&')
r.get("mykey")
r.set("anotherkey", "anothervalue")
r.get("anotherkey")

