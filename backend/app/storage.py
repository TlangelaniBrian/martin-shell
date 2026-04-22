import boto3


class PDFStorage:
    def __init__(self, settings):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
        )
        self.bucket = settings.r2_bucket_name

    def upload_pdf(self, key: str, data: bytes) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType="application/pdf",
        )
        return key

    def download_pdf(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def get_pdf_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def make_key(self, court: str, year: int, filename: str) -> str:
        return f"cases/{court}/{year}/{filename}.pdf"
