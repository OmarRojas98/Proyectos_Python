import boto3
from pydantic import BaseModel

from config.settings import settings
from constants import KINESIS_FIREHOSE_MAX_RECORDS
from services.aws_kinesis_eliminar.data_streams import KinesisStream


def append_record(records: list, new_record: BaseModel):
    records.append({
        'Data': new_record.model_dump_json(),
        'PartitionKey': new_record.name
    })


def batch_stream_to_firehose(records_list: list[BaseModel]):
    data_stream_client = boto3.client(
        'kinesis',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION
    )
    data_stream = KinesisStream(data_stream_client)
    data_stream.describe(name=settings.KINESIS_DATA_STREAM)
    records = []
    for company in records_list:
        if len(records) < KINESIS_FIREHOSE_MAX_RECORDS:
            append_record(records, company)
        else:
            data_stream.put_records(records)
            records = list()
            append_record(records, company)
    if len(records) > 0:
        data_stream.put_records(records)
    print("Successfully finished")
