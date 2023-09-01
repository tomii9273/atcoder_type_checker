#!/bin/sh
cd app && gunicorn app:app --log-file=-
