from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord


# 返回正确Json
def sucResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

# 返回错误Json
def errorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

# 点赞后台处理
def like_change(request):
    # 获取数据并验证
    user = request.user
    if not user.is_authenticated:
        return errorResponse(400, '用户未登录')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_clz = content_type.model_class()
        model_obj = model_clz.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return errorResponse(401, '对象不存在')

    # 处理数据
    if request.GET.get('is_like') == 'true':        # 这里注意python的True和Ajax的true
        # 要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            # 未点赞过，进行点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return sucResponse(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return errorResponse(402, '已点赞过，不能重复点赞')

    else:
        # 取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数-1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return sucResponse(like_count.liked_num)
            else:
                return errorResponse(404, '数据错误')
        else:
            # 没有点赞过，不能取消
            return errorResponse(403, '未点赞过，不能取消点赞')
