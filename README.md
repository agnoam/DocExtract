# Docx extraction service
This service used to extract text from MS Word documents (.docx) by it's styles. <br/>
It listens to a wating documents queue, <br/>
After the file download. <br/>
The service will tare down the document, and save the results into the SQL database.

## Dependencies:
* RabbitMQ
* MySQL
* S3 (minio)

## Queues used:
* `WATING_DOCX` - Queue that holds the documents S3 bucket links

## Tests
This service includes unit testings for auto deployment