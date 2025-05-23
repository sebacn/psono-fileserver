from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from django.conf import settings
import shutil
import json
import binascii
import nacl.signing


def generate_signature():
        
    SHARDS_PUB = []
    min_disk_space = settings.HEALTHCHECK_MIN_DISK_SPACE

    for s in settings.SHARDS:
        shard_status_info = {}
        shard_status = True
        if s['engine']['class'] == 'local' and 'location' in s['engine']['kwargs']:
            storage_path = s['engine']['kwargs']['location']

            try:
                # Get disk usage statistics for the path
                disk_usage = shutil.disk_usage(storage_path)
                free_space = disk_usage.free
                
                # Check if available space is below the minimum threshold
                if free_space < min_disk_space:
                    shard_status = False
                    shard_status_info = {
                        'status': 'Warning: Low disk space',
                        'free_space_mb': round(free_space / (1024 * 1024), 2),
                        'min_required_mb': round(min_disk_space / (1024 * 1024), 2)
                    }
                else:
                    shard_status_info = {
                        'status': 'Ok',
                        'free_space_mb': round(free_space / (1024 * 1024), 2),
                        'min_required_mb': round(min_disk_space / (1024 * 1024), 2)
                    }
            except (FileNotFoundError, PermissionError, OSError) as e:
                # Handle errors in accessing the storage path
                shard_status = False
                shard_status_info = {
                    'status': 'Error: Storage path access failed',
                    'error': str(e)
                }

        SHARDS_PUB.append({
            'shard_id': s['shard_id'],
            'read': s['read'] and settings.READ,
            'write': s['write'] and settings.WRITE,
            'delete': s['delete'] and settings.DELETE,
            'allow_link_shares': s.get('allow_link_shares', 'True') and settings.ALLOW_LINK_SHARES,
            'status': {
                'healthy': shard_status,
                'details': shard_status_info
                }
        })

    info = {
        'version': settings.VERSION,
        'fileserver_id': settings.FILESERVER_ID,
        'api': 1,
        'public_key': settings.PUBLIC_KEY,
        'cluster_id': settings.CLUSTER_ID,
        'shards': SHARDS_PUB,
        'read': settings.READ,
        'write': settings.WRITE,
        'delete': settings.DELETE,
        'allow_link_shares': settings.ALLOW_LINK_SHARES,
        'host_url': settings.HOST_URL,
    }

    infostr = json.dumps(info)

    signing_box = nacl.signing.SigningKey(settings.PRIVATE_KEY, encoder=nacl.encoding.HexEncoder)
    verify_key = signing_box.verify_key.encode(encoder=nacl.encoding.HexEncoder)
    # The first 128 chars (512 bits or 64 bytes) are the actual signature, the rest the binary encoded info
    signature = binascii.hexlify(signing_box.sign(infostr.encode()))[:128]

    return {
        'info': info,
        'signature': signature,
        'verify_key': verify_key,
    }

class InfoView(GenericAPIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('GET', 'OPTIONS', 'HEAD')
    throttle_scope = 'health_check'

    def get(self, request, *args, **kwargs):
        """
        Returns the Server's signed information

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        return Response(generate_signature(), status=status.HTTP_200_OK)

    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)