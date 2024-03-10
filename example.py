import json

data = {
    'name': 'person1',
    'taxes': 'due soon'
}

files = [{ 'filename' : 'file1' , 'data' : 1}, { 'filename' : 'file1' , 'data' : 4} ]

file_fields = [{'fileName' : file['filename'], 'data': file['data']} for file in files]
files_fields = {**data, **{'files': file_fields}}
payload = json.dumps(files_fields)

payload = json.loads(payload)

for file_list in payload['files']:
    print(file_list['fileName'])
    print(file_list['data'])
    print()

