import json
import logging
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"String diterima: {string_datamasuk}")
        s = string_datamasuk.strip()
        try:
            if not s:
                return json.dumps({'status':'ERROR','data':'Empty input'})
            parts = s.split(' ', 2)
            c_request = parts[0].lower()
            logging.warning(f"memproses request: {c_request}")

            if c_request == 'upload':
                if len(parts) < 3:
                    return json.dumps({'status':'ERROR','data':'Format UPLOAD tidak sesuai'})
                filename = parts[1]
                file_content = parts[2]
                logging.warning(f"Proses upload file: {filename}, ukuran konten: {len(file_content)} karakter")
                res = self.file.upload([filename, file_content])
                return json.dumps(res)

            elif c_request == 'get':
                if len(parts) < 2:
                    return json.dumps({'status':'ERROR','data':'Format GET tidak sesuai'})
                res = self.file.get([parts[1]])
                return json.dumps(res)

            elif c_request == 'list':
                res = self.file.list([])
                return json.dumps(res)

            elif c_request == 'delete':
                if len(parts) < 2:
                    return json.dumps({'status':'ERROR','data':'Format DELETE tidak sesuai'})
                res = self.file.delete([parts[1]])
                return json.dumps(res)

            else:
                return json.dumps({'status':'ERROR','data':'Unknown command'})

        except Exception as e:
            logging.error(f"Terjadi kesalahan saat memproses: {e}")
            return json.dumps({'status':'ERROR','data':str(e)})

if __name__ == '__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))
