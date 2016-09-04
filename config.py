# coding: utf-8

from models.utils_helper import filter_request


class RewriteCfg():
    def __init__(self):
        # 白名单
        self.white_list_filepath = './data/white_list.txt'
        # 商圈列表
        self.business_area_filepath = './data/ba.txt'
        # 地区列表
        self.region_filepath = './data/all_region.txt'
        # 各地点击权重
        self.click_threshold_filepath = './data/click.txt'
        self.default_click_threshold = 2200
        # 省、城市列表
        self.city_list_filepath = './data/city_prov.txt'
        # self.soso_srv_ip=['10.231.128.173:10081', '10.229.133.21:10081'],
        self.soso_srv_ip = ['apis.map.qq.com']
        self.soso_srv_appkey = 'DJYBZ-MKKH5-QXIID-QBJNE-SAKGT-IFBNJ'
        self.soso_conn_timeout = 0.2
        self.soso_timeout = 0.5
        self.isready = self.prepare()

    def load_white_list(self):
        self.white_list = []
        with open(self.white_list_filepath, 'r') as fr:
            for line in fr:
                arr = line.strip().split('\t')
                try:
                    if len(arr) != 8:
                        # TODO: log out when fail to read
                        continue
                    area, name, addr, blng, blat, slng, slat, opt = (x for x in arr)
                    area = int(area)
                    name = name.decode('utf-8')
                    addr = addr.decode('utf-8')
                    blng, blat = float(blng), float(blat)
                    slng, slat = float(slng), float(slat)
                    opt = int(opt)
                    if filter_request(area, name, addr, blng, blat, slng, slat):
                        continue
                    self.white_list.append((int(area), name, addr, blng, blat, slng, slat, opt))
                except:
                    continue
        return True

    def load_business_area_list(self):
        self.ba = {}
        with open(self.business_area_filepath, 'r') as fr:
            for line in fr:
                arr = line.strip().split('\t')
                try:
                    area, city, name, slng, slat = (x for x in arr)
                    area = int(area)
                    if area not in self.ba:
                        self.ba[area] = []
                    self.ba[area].append((name.decode('utf-8'), float(slng), float(slat)))
                except:
                    continue
        return True

    def load_region_list(self):
        self.region_list = {}
        with open(self.region_filepath, 'r') as fr:
            for line in fr:
                region_name = line.strip().decode('utf-8')
                self.region_list[region_name] = 1
        return True

    def load_city_list(self):
        self.cities = {}
        with open(self.city_list_filepath, 'r') as fr:
            for line in fr:
                city = line.strip().decode('utf-8')
                self.cities[city] = 1
        return True

    def load_click_threshold(self):
        self.click_threshold_by_area = {}
        with open(self.click_threshold_filepath, 'r') as fr:
            for line in fr:
                arr = line.strip().split('\t')
                if len(arr) != 2:
                    continue
                try:
                    area, click = int(arr[0]), int(arr[1])
                except:
                    continue
                self.click_threshold_by_area[area] = click
        return True

    def prepare(self):
        if not self.load_white_list():
            self.last_error = 'failed to load white list data'
            return False

        if not self.load_business_area_list():
            self.last_error = 'failed to load business area data'
            return False

        if not self.load_region_list():
            self.last_error = 'failed to load region data'
            return False

        if not self.load_city_list():
            self.last_error = 'failed to load city data'
            return False

        if not self.load_click_threshold():
            self.last_error = 'failed to load click data'
            return False

        return True


g_cfg = RewriteCfg()

if __name__ == '__main__':
    print g_cfg.isready
