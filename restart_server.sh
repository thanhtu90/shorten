#!/bin/bash
python clear_cache.py
sudo service gunicorn restart
sudo service nginx restart
