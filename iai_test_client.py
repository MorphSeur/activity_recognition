# -*- coding: utf-8 -*-
import os
import requests
from argparse import ArgumentParser
from cryptography.fernet import Fernet

# request_body = {
#   "session_id": "SESSION_ID_PLACEHOLDER", 
#   "iai_datalake": "IAI_DATALAKE_PLACEHOLDER", 
#   "iai_datacipher": "base64", 
#   "iai_datakey": None, 
#   "iai_files": ["IAI_FILE_PLACEHOLDER.dpo"], 
#   "on_finish_url": "ON_FINISH_URL_PLACEHOLDER", 
#   "iai_params": {}, 
#   "iai_dpo_metadata": [
#     {
#       "id": "IAI_FILE_ID_PLACEHOLDER", 
#       "dsa_id": "IAI_FILE_DSA_ID_PLACEHOLDER", 
#       "start_time": "IAI_FILE_START_TIME_PLACEHOLDER",
#       "end_time": "IAI_FILE_END_TIME_PLACEHOLDER", 
#       "event_type": "IAI_FILE_EVENT_TYPE_PLACEHOLDER",
#       "organization": "IAI_FILE_ORGANIZATION_PLACEHOLDER",
#       "file:extension": "IAI_FILE_FILE_EXTENSION_PLACEHOLDER",
#       }
#   ]
# }

# TODO: Update data in request_body
request_body = {
   "session_id":"4231a42c-aa79-413e-93a6-35757257a59c",
   "iai_datalake":"/raid/home/labuseraber/environment/testEnvironment/activityRecognition/iai-skeleton-v1.4.2/tmp/iai",
   "iai_datacipher":"base64",
   "iai_datakey":None,
   "iai_files":[
      "video.dpo"
   ],
   "on_finish_url":None,
   "iai_params":{
      
   },
   "iai_dpo_metadata":[
      {
         "id":"1663142001174-9dc345df-78ed-45c5-b379-257b60681a61",
         "dsa_id":"DSA-26e30e52-18b5-4feb-9281-7af3962d97ce",
         "start_time":"2022-09-20T10:01:09Z",
         "end_time":"2022-09-20T11:01:09Z",
         "event_type":"_event_type",
         "organization":"CNR",
         "file:extension":"avi"
      }
   ]
}

def send_start(args):
  url = "{}/startAnalytics".format(args.target)
 
  payload = dict(
    session_id=request_body["session_id"],
    iai_datalake=request_body["iai_datalake"],
    iai_datacipher=request_body["iai_datacipher"],
    iai_datakey=request_body["iai_datakey"],
    iai_files=request_body["iai_files"],
    on_finish_url=None,
    iai_params=request_body["iai_params"],
    iai_dpo_metadata=request_body["iai_dpo_metadata"]
    )

  if request_body["iai_datakey"] is not None:
    encfilenames = encrypt_datalake(payload["iai_datakey"], payload["iai_datalake"], payload["iai_files"])
    payload["iai_files"] = encfilenames

  ret = requests.post(url, json=payload)
  print("Server response: [status={}, body={}]".format(ret.status_code, ret.json() if ret.status_code == 200 else ret.content.decode('UTF-8')))

def send_stop(args):
  url = "{}/stopAnalytics".format(args.target)

  ret = requests.put(url, params={'session_id': args.session_id})
  print("Server response: [status={}, body={}]".format(ret.status_code, ret.json() if ret.status_code == 200 else ret.content.decode('UTF-8')))


def encrypt_datalake(key, datalake_dir, files):
  """
  Encrypts the files provided in datalake in order to be used in IAI agent

  Parameters:
  key The key to use for encrypt files
  datalake_dir Directory of the datalake
  files array of filenames to use in analytics

  Return: Encryption key
  """
  f = Fernet(key)
  print("== Prepare datalake ==")

  for filename in files:
    print("- encrypt: {}...".format(filename))
    with open(os.path.join(datalake_dir, filename), 'rb') as fin:
      with open(os.path.join(datalake_dir, filename + '.enc'), 'wb') as fout:
        fout.write(f.encrypt(fin.read()))

  encfilenames = [fname + '.enc' for fname in files]

  return encfilenames


def main():
  p = ArgumentParser()
  p.add_argument('--target', '-t', default='http://localhost:5000', help="Address where iai agent server is running")
  
  subparsers = p.add_subparsers(help='Available action', dest='action')
  p_start = subparsers.add_parser('start')

  p_stop = subparsers.add_parser('stop')
  p_stop.add_argument('--session-id', default='1234', help="Session id to be used")

  args = p.parse_args()

  if args.action == 'start':
    send_start(args)
  elif args.action == 'stop':
    send_stop(args)


if __name__ == '__main__':
  main()
