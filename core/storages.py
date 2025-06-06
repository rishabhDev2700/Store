from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = True
    access_key = settings.AWS_S3_ACCESS_KEY_ID
    secret_key = settings.AWS_S3_SECRET_ACCESS_KEY
    bucket_name = settings.AWS_S3_BUCKET_NAME
    custom_domain = settings.MEDIA_HOST
    querystring_auth = False
