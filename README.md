# Activity Recognition - With Encryption - DPO Decoding
## [server.py](https://github.com/MorphSeur/activity_recognition/blob/main/server.py)
The version of the IAI-skeleton is 1.4.2.    
The activity recognition library is integrated with the new trained models - lissilab.  
[server.py](https://github.com/MorphSeur/activity_recognition/blob/main/server.py) performs decoding of .dpo files, and activity recognition.

To run an example:
- Start the analytic server:
    ```sh
    $ python server.py
    ```
- Querying the server when using video input:
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:50000 start
    ```
- Stop the analytic:
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:50000 stop
    ```

## Requirements
- Please refer to [requirements.txt](https://github.com/MorphSeur/activity_recognition/blob/main/requirements.txt).
- Python 3.7.7 was used.

## Dockerfile
Dockerfile contains necessary libraries to face recognition analytic.
- To build the docker
    ```
    $ sudo docker build --tag activity_recognition .
    ```
- To run the analytic
    ```
    $ sudo docker run --publish 50000:50000 --volume="/path/to/tmp/testiai/:/path/to/tmp/testiai/" -v $(pwd):/app activity_recognition sh /app/docker-entrypoint.sh
    ```