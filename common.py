from urllib import request
import json, uuid


class common:

    def get(self, api_url):
        print(api_url)
        response = request.urlopen(api_url, timeout=1)
        response = response.read().decode('utf8')
        if isinstance(response, str):
            if self.is_json(response):
                json_string = json.loads(response)
                if json_string != 0 and json_string['code'] == 0:
                    print("CODE: %s, ERROR: %s" % (json_string['error'], json_string['info']))
                    return False
                return json_string
        return False

    def is_json(self, response):
        if response == '0':
            return False
        if isinstance(response, str):
            try:
                json.loads(response)
                return True
            except ValueError as e:
                return False

    def serial(self):
        outfile = "serial.dat"
        if not os.path.isfile(outfile):
            file = open(outfile, "w")
            serial_string = str(uuid.uuid4()).replace("-", "")
            file.write(serial_string)
            file.close()
        else:
            file = open(outfile, "r")
            serial_string = file.read()

        return serial_string

    def download(self, url):
        file_name = os.path.basename(url)
        file_path = "download/%s" % time.strftime("%Y/%m/%d", time.localtime())
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        outfile = "%s/%s" % (file_path, file_name)
        if not os.path.isfile(outfile):
            request.urlretrieve(url, outfile)
        print(outfile)
        return outfile