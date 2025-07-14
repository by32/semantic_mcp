-- Configure DuckDB in Cube.js container to use MinIO
INSTALL httpfs;
LOAD httpfs;

-- Configure S3 settings for MinIO
SET s3_endpoint='minio:9000';
SET s3_access_key_id='admin';
SET s3_secret_access_key='password123';
SET s3_use_ssl=false;
SET s3_url_style='path';

-- Test connection
SELECT COUNT(*) as test_connection FROM read_parquet('s3://semantic-lake/cities.parquet');