from minio import Minio

minioClient = Minio('http://127.0.0.1:9500',
              access_key='Chasey',
              secret_key='ChaseyMinIO',
              secure=True)

print(minioClient.list_buckets())