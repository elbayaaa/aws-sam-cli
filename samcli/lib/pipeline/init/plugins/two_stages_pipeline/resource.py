""" AWS resource represented by ARN"""
from typing import Optional


class Resource:
    def __init__(self, arn: str):
        self.arn: str = arn
        self.is_user_provided: bool = True if arn else False

    def name(self):
        if not self.arn:
            return None
        else:
            return self.arn.split(":")[-1]


class Deployer(Resource):
    def __init__(self, arn: str, access_key_id: Optional[str] = None, secret_access_key: Optional[str] = None):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        super().__init__(arn=arn)


class S3Bucket(Resource):
    def __init__(self, arn: str, kms_key_arn: Optional[str] = None):
        self.kms_key_arn = kms_key_arn
        super().__init__(arn=arn)
