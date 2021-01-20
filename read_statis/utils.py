import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail

def read_statis_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)     # 这里传入类或对象都可以
    key = '%s_%s_read' % (ct.model, obj.pk)
    # 没有读过的情况下才将阅读次数+1
    if not request.COOKIES.get(key):

        # 总阅读计数+1
        readNum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readNum.read_num += 1
        readNum.save()

        # 关联日期的阅读计数+1
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num +=1
        readDetail.save()
    return key

def get_7days_read_data(content_type):
    today = timezone.now().date()
    readNums = []
    dates = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        readDetails = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = readDetails.aggregate(read_num_sum = Sum('read_num'))
        readNums.append(result['read_num_sum'] or 0)
    return dates, readNums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:7]