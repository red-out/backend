from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('web', image_name, file_object, file_object.size)
        return f"http://{settings.AWS_S3_ENDPOINT_URL}/web/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic(new_stock, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
    )
    i = new_stock.id
    img_obj_name = f"{i}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения логотипа."})

    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    new_stock.image_url = result  # Убедитесь, что вы используете правильное поле
    new_stock.save()

    return Response({"message": "success"})
def delete_pic(stock):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    img_obj_name = f"{stock.id}.png"

    try:
        client.remove_object('web', img_obj_name)
        return {"message": "Image deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete image: {str(e)}"}

