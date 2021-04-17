import boto3

def s3Creds():
    s3 = boto3.resource('s3', 
                        region_name='ap-south-1', 
                        aws_access_key_id='***key***',
                        aws_secret_access_key='***secret***')
    bucket = s3.Bucket('***bucketName***')

    return bucket

list = []
for obj in s3Creds().objects.all():
    list.append(obj.key)
    
#response = object.get(file_stream)

#plt.figure(0)
#plt.imshow(image)
#print(tP(iP(image)))