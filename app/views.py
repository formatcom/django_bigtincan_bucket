import requests, os, unicodedata

from io import BytesIO
from django.http import JsonResponse, HttpResponse, Http404
from PIL import Image
from pilkit.processors import SmartResize
from requests_toolbelt import MultipartEncoder

from .models import ImageTest

# deberia estar en settings :3 desde env
SERVER_BUCKET = 'https://pubapi.bigtincan.com'

# para limpiar caracteres especiales
# bigtincan da problema con ellos
def normalize(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def view_upload_test(request, bucket, token):
    BUCKET_UPlOAD_FILE = '{}/alpha/story/upload/file'.format(SERVER_BUCKET)

    instance = ImageTest.objects.first()
    if not instance:
        raise Http404

    image_name = os.path.basename(instance.image.name)
    image = Image.open(BytesIO(instance.image.read()))


    processor = SmartResize(256, 256)
    image_result = processor.process(image)

    image_data = BytesIO()
    image_result.save(image_data, format=image.format)

    image.close()

    m = MultipartEncoder(
        fields = {
            'upload_type':'file',
            'files': (
                normalize(image_name),
                image_data.getvalue(),
                image_result.format,
            ),
        },
    )

    response = requests.request(
        'post',
        BUCKET_UPlOAD_FILE,
        data = m,
        headers = {
            'authorization': 'Bearer {}'.format(token),
            'Content-Type': m.content_type,
        },
    )

    r_filename = None
    r_description = None
    if response.status_code == requests.codes.ok:
        obj = response.json()
        r_filename = obj['data'][0]['filename']
        r_description = obj['data'][0]['description']

        # estructura del bucket privado de bigtincan
        # https://{servidor}/f/{bucket_id}/upload/{filename}
        # https://pubapi.bigtincan.com/f/{bucket_id}/upload/

        instance.image_url = '{}/f/{}/upload/{}'.format(
            SERVER_BUCKET,
            bucket,
            r_filename,
        )

        # eliminamos el archivo del disco
        instance.image.delete(save=True)

    response.close()
    image_result.close()

    if not instance.image.closed:
        instance.image.close()

    return JsonResponse({
        'token': token,
        'name': image_name,
        'filename': r_filename,
        'description': r_description,
        'file_url': instance.image_url,
    })

def view_get_file(request):

    instance = ImageTest.objects.first()
    if not instance:
        raise Http404

    template = '<img src="{}" />'

    if not instance.image:
        template = template.format(instance.image_url)
    else:
        template = template.format(instance.image.url)

    return HttpResponse(template)
