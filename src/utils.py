from datetime import datetime, timedelta

def localtime_utc_delta():
    # NOTE: This will only work if the total execution time of now() and utcnow() is shorter than 60 seconds
    minutes_between_utc_and_localtime = round((datetime.now() - datetime.utcnow()).total_seconds() / 60.0)
    return timedelta(0, minutes_between_utc_and_localtime * 60)

def utc_to_localtime(timestamp):
    return timestamp + localtime_utc_delta()

def localtime_to_utc(timestamp):
    return timestamp - localtime_utc_delta()
