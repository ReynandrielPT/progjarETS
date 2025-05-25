import os
import json
import base64
import logging
from glob import glob

class FileInterface:
    def __init__(self):
        os.chdir('files/')

    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))


    def get(self,params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fp = open(f"{filename}",'rb')
            isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK',data_namafile=filename,data_file=isifile)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def upload(self, params=[]):
        try:
            if len(params) != 2:
                return dict(status='ERROR', data='Need filename and file content parameters')

            filename = params[0]
            file_content = params[1]

            logging.warning(f"Uploading file: {filename}")

            try:
                content = base64.b64decode(file_content)
            except Exception as e:
                logging.error("Error decoding base64")
                return dict(status='ERROR', data=str(e))

            with open(filename, 'wb+') as fp:
                fp.write(content)

            os.chmod(filename, 0o755)            
            
            logging.warning(f"File {filename} uploaded successfully ({len(content)} bytes)")
            return dict(status='OK', data_namafile=filename)

        except Exception as e:
            logging.error(f"Error in upload: {str(e)}")
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            if filename == '':
                return dict(status='ERROR', data='Filename cannot be empty')

            logging.warning(f"Deleting file: {filename}")

            if not os.path.exists(filename):
                return dict(status='ERROR', data=f'File {filename} cannot be found')

            os.remove(filename)
            logging.warning(f"File {filename} deleted successfully")
            return dict(status='OK', data_namafile=filename)
        except Exception as e:
            logging.error(f"Error in delete: {str(e)}")
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))
