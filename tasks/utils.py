import datetime as dt, pytz
from prefect import task

@task
def get_date_ranges():
    today_et = dt.datetime.today().astimezone(pytz.timezone('US/Eastern')).date()
    date_range_dict = {}
    date_range_dict['today_et'] = today_et
    date_range_dict['schedule_start_date'] = today_et - dt.timedelta(days=1)
    date_range_dict['schedule_end_date'] = today_et + dt.timedelta(days=3)
    date_range_dict['boxscore_start_date'] = today_et - dt.timedelta(days=3)
    date_range_dict['boxscore_end_date'] = today_et
    return date_range_dict