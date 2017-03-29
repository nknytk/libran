# coding: utf-8

import os
import re
import sys
from urllib.request import urlopen
import bs4
sys.path.append(os.path.dirname(__file__))
from base import Command

AREAS = {
    # 北海道
    '宗谷': {'name': '宗谷地方', 'area_id': '301', 'row_index': 0},
    '稚内': {'name': '稚内', 'area_id': '301', 'row_index': 0},
    '川上': {'name': '川上地方', 'area_id': '302', 'row_index': 0},
    '旭川': {'name': '旭川', 'area_id': '302', 'row_index': 0},
    '留萌': {'name': '留萌', 'area_id': '302', 'row_index': 1},
    '網走': {'name': '網走', 'area_id': '303', 'row_index': 0},
    '北見': {'name': '北見', 'area_id': '303', 'row_index': 1},
    '紋別': {'name': '紋別', 'area_id': '303', 'row_index': 2},
    '根室': {'name': '根室', 'area_id': '304', 'row_index': 0},
    '釧路': {'name': '釧路', 'area_id': '304', 'row_index': 1},
    '十勝': {'name': '十勝', 'area_id': '304', 'row_index': 2},
    '帯広': {'name': '帯広', 'area_id': '304', 'row_index': 2},
    '胆振': {'name': '胆振', 'area_id': '305', 'row_index': 0},
    '室蘭': {'name': '室蘭', 'area_id': '305', 'row_index': 0},
    '日高': {'name': '日高', 'area_id': '305', 'row_index': 1},
    '浦河': {'name': '浦河', 'area_id': '305', 'row_index': 1},
    '石狩': {'name': '石狩', 'area_id': '306', 'row_index': 0},
    '札幌': {'name': '札幌', 'area_id': '306', 'row_index': 0},
    '空知': {'name': '空知', 'area_id': '306', 'row_index': 1},
    '岩見沢': {'name': '岩見沢', 'area_id': '306', 'row_index': 1},
    '後志': {'name': '後志', 'area_id': '306', 'row_index': 2},
    '倶知安': {'name': '倶知安', 'area_id': '306', 'row_index': 2},
    '渡島': {'name': '渡島', 'area_id': '307', 'row_index': 0},
    '函館': {'name': '函館', 'area_id': '307', 'row_index': 0},
    '檜山': {'name': '檜山', 'area_id': '307', 'row_index': 1},
    '江差': {'name': '江差', 'area_id': '307', 'row_index': 1},
    # 青森県
    '津軽': {'name': '津軽', 'area_id': '308', 'row_index': 0},
    '青森': {'name': '青森', 'area_id': '308', 'row_index': 0},
    '深浦': {'name': '深浦', 'area_id': '308', 'row_index': 0},
    '下北': {'name': '下北', 'area_id': '308', 'row_index': 1},
    'むつ': {'name': 'むつ', 'area_id': '308', 'row_index': 1},
    '三八上北': {'name': '三八上北', 'area_id': '308', 'row_index': 2},
    '八戸': {'name': '八戸', 'area_id': '308', 'row_index': 2},
    # 秋田県
    '秋田': {'name': '秋田', 'area_id': '309', 'row_index': 0},
    '横手': {'name': '横手', 'area_id': '309', 'row_index': 1},
    '鷹巣': {'name': '鷹巣', 'area_id': '309', 'row_index': 1},
    # 岩手県
    '岩手': {'name': '岩手', 'area_id': '310', 'row_index': 0},
    '盛岡': {'name': '盛岡', 'area_id': '310', 'row_index': 0},
    '二戸': {'name': '二戸', 'area_id': '310', 'row_index': 0},
    '一関': {'name': '一関', 'area_id': '310', 'row_index': 0},
    '宮古': {'name': '宮古', 'area_id': '310', 'row_index': 1},
    '大船渡': {'name': '大船渡', 'area_id': '310', 'row_index': 2},
    # 山形県
    '山形': {'name': '山形', 'area_id': '311', 'row_index': 0},
    '村山': {'name': '村山', 'area_id': '311', 'row_index': 0},
    '米沢': {'name': '米沢', 'area_id': '311', 'row_index': 1},
    '置賜': {'name': '置賜', 'area_id': '311', 'row_index': 1},
    '庄内': {'name': '庄内', 'area_id': '311', 'row_index': 2},
    '酒田': {'name': '酒田', 'area_id': '311', 'row_index': 2},
    '最上': {'name': '最上', 'area_id': '311', 'row_index': 3},
    '新庄': {'name': '新庄', 'area_id': '311', 'row_index': 3},
    # 宮城県
    '宮城': {'name': '宮城', 'area_id': '312', 'row_index': 0},
    '仙台': {'name': '仙台', 'area_id': '312', 'row_index': 0},
    '古川': {'name': '古川', 'area_id': '312', 'row_index': 0},
    '石巻': {'name': '石巻', 'area_id': '312', 'row_index': 0},
    '白石': {'name': '白石', 'area_id': '312', 'row_index': 1},
    # 福島県
    '福島': {'name': '福島', 'area_id': '313', 'row_index': 0},
    '中通り': {'name': '中通り', 'area_id': '313', 'row_index': 0},
    '郡山': {'name': '郡山', 'area_id': '313', 'row_index': 0},
    '白河': {'name': '白河', 'area_id': '313', 'row_index': 0},
    '浜通り': {'name': '浜通り', 'area_id': '313', 'row_index': 1},
    '小名浜': {'name': '小名浜', 'area_id': '313', 'row_index': 1},
    '相馬': {'name': '相馬', 'area_id': '313', 'row_index': 1},
    '会津': {'name': '会津', 'area_id': '313', 'row_index': 2},
    '若松': {'name': '若松', 'area_id': '313', 'row_index': 2},
    '田島': {'name': '田島', 'area_id': '313', 'row_index': 2},
    # 茨城県
    '茨城': {'name': '茨城', 'area_id': '314', 'row_index': 0},
    '水戸': {'name': '水戸', 'area_id': '314', 'row_index': 0},
    '土浦': {'name': '土浦', 'area_id': '314', 'row_index': 1},
    # 群馬県
    '群馬': {'name': '群馬', 'area_id': '315', 'row_index': 0},
    '前橋': {'name': '前橋', 'area_id': '315', 'row_index': 0},
    'みなかみ': {'name': 'みなかみ', 'area_id': '315', 'row_index': 1},
    '水上': {'name': '水上', 'area_id': '315', 'row_index': 1},
    # 栃木県
    '栃木': {'name': '栃木', 'area_id': '316', 'row_index': 0},
    '宇都宮': {'name': '宇都宮', 'area_id': '316', 'row_index': 0},
    '大田原': {'name': '大田原', 'area_id': '316', 'row_index': 1},
    # 埼玉県
    '埼玉': {'name': '埼玉', 'area_id': '317', 'row_index': 0},
    'さいたま': {'name': 'さいたま', 'area_id': '317', 'row_index': 0},
    '熊谷': {'name': '熊谷', 'area_id': '317', 'row_index': 0},
    '秩父': {'name': '秩父', 'area_id': '317', 'row_index': 1},
    # 千葉県
    '千葉': {'name': '千葉', 'area_id': '318', 'row_index': 0},
    '銚子': {'name': '銚子', 'area_id': '318', 'row_index': 1},
    '館山': {'name': '館山', 'area_id': '318', 'row_index': 2},
    # 東京都
    '東京': {'name': '東京', 'area_id': '319', 'row_index': 0},
    '伊豆諸島': {'name': '伊豆諸島', 'area_id': '319', 'row_index': 1},
    '小笠原': {'name': '小笠原諸島', 'area_id': '319', 'row_index': 3},
    '父島': {'name': '父島', 'area_id': '319', 'row_index': 3},
    # 神奈川県
    '神奈川': {'name': '神奈川', 'area_id': '320', 'row_index': 0},
    '横浜': {'name': '横浜', 'area_id': '320', 'row_index': 0},
    '小田原': {'name': '小田原', 'area_id': '320', 'row_index': 1},
    # 山梨県
    '山梨': {'name': '山梨', 'area_id': '321', 'row_index': 0},
    '甲府': {'name': '甲府', 'area_id': '321', 'row_index': 0},
    '富士': {'name': '富士', 'area_id': '321', 'row_index': 1},
    '河口湖': {'name': '河口湖', 'area_id': '321', 'row_index': 1},
    # 長野県
    '長野': {'name': '長野', 'area_id': '322', 'row_index': 0},
    '松本': {'name': '松本', 'area_id': '323', 'row_index': 1},
    '諏訪': {'name': '諏訪', 'area_id': '323', 'row_index': 1},
    '軽井沢': {'name': '軽井沢', 'area_id': '323', 'row_index': 1},
    '飯田': {'name': '飯田', 'area_id': '323', 'row_index': 2},
    # 新潟県
    '新潟': {'name': '新潟', 'area_id': '323', 'row_index': 0},
    '津川': {'name': '津川', 'area_id': '323', 'row_index': 0},
    '下越': {'name': '下越', 'area_id': '323', 'row_index': 0},
    '中越': {'name': '中越', 'area_id': '323', 'row_index': 1},
    '長岡': {'name': '長岡', 'area_id': '323', 'row_index': 1},
    '湯沢': {'name': '湯沢', 'area_id': '323', 'row_index': 1},
    '下越': {'name': '下越', 'area_id': '323', 'row_index': 2},
    '高田': {'name': '高田', 'area_id': '323', 'row_index': 2},
    '佐渡': {'name': '佐渡', 'area_id': '323', 'row_index': 3},
    '相川': {'name': '相川', 'area_id': '323', 'row_index': 3},
    # 富山県
    '富山': {'name': '富山', 'area_id': '324', 'row_index': 0},
    '伏木': {'name': '伏木', 'area_id': '324', 'row_index': 1},
    # 石川県
    '石川': {'name': '石川', 'area_id': '325', 'row_index': 0},
    '加賀': {'name': '加賀', 'area_id': '325', 'row_index': 0},
    '金沢': {'name': '金沢', 'area_id': '325', 'row_index': 0},
    '能登': {'name': '能登', 'area_id': '325', 'row_index': 1},
    '輪島': {'name': '輪島', 'area_id': '325', 'row_index': 1},
    # 福井県
    '福井': {'name': '福井', 'area_id': '326', 'row_index': 0},
    '大野': {'name': '大野', 'area_id': '326', 'row_index': 0},
    '嶺北': {'name': '嶺北', 'area_id': '326', 'row_index': 0},
    '嶺南': {'name': '嶺南', 'area_id': '326', 'row_index': 1},
    '敦賀': {'name': '敦賀', 'area_id': '326', 'row_index': 1},
    # 静岡県
    '静岡': {'name': '静岡', 'area_id': '327', 'row_index': 0},
    '伊豆': {'name': '伊豆', 'area_id': '327', 'row_index': 1},
    '綱代': {'name': '綱代', 'area_id': '327', 'row_index': 1},
    '石廊崎': {'name': '石廊崎', 'area_id': '327', 'row_index': 1},
    '三島': {'name': '三島', 'area_id': '327', 'row_index': 2},
    '浜松': {'name': '浜松', 'area_id': '327', 'row_index': 3},
    '御前崎': {'name': '御前崎', 'area_id': '327', 'row_index': 3},
    # 岐阜県
    '岐阜': {'name': '岐阜', 'area_id': '328', 'row_index': 0},
    '美濃': {'name': '美濃', 'area_id': '328', 'row_index': 0},
    '飛騨': {'name': '飛騨', 'area_id': '328', 'row_index': 1},
    '高山': {'name': '高山', 'area_id': '328', 'row_index': 1},
    # 愛知県
    '愛知': {'name': '愛知', 'area_id': '329', 'row_index': 0},
    '名古屋': {'name': '名古屋', 'area_id': '329', 'row_index': 0},
    '豊橋': {'name': '豊橋', 'area_id': '329', 'row_index': 1},
    # 三重県
    '三重': {'name': '三重', 'area_id': '330', 'row_index': 0},
    '津': {'name': '津', 'area_id': '330', 'row_index': 0},
    '四日市': {'name': '四日市', 'area_id': '330', 'row_index': 0},
    '尾鷲': {'name': '尾鷲', 'area_id': '330', 'row_index': 1},
    # 大阪
    '大阪': {'name': '大阪', 'area_id': '331', 'row_index': 0},
    # 兵庫県
    '兵庫': {'name': '兵庫', 'area_id': '332', 'row_index': 0},
    '神戸': {'name': '神戸', 'area_id': '332', 'row_index': 0},
    '姫路': {'name': '姫路', 'area_id': '332', 'row_index': 0},
    '洲本': {'name': '洲本', 'area_id': '332', 'row_index': 0},
    '豊岡': {'name': '豊岡', 'area_id': '332', 'row_index': 1},
    # 京都府
    '京都': {'name': '京都', 'area_id': '333', 'row_index': 0},
    '舞鶴': {'name': '舞鶴', 'area_id': '333', 'row_index': 1},
    # 滋賀県
    '滋賀': {'name': '滋賀', 'area_id': '334', 'row_index': 0},
    '大津': {'name': '大津', 'area_id': '334', 'row_index': 0},
    '彦根': {'name': '彦根', 'area_id': '334', 'row_index': 1},
    # 奈良県
    '奈良': {'name': '奈良', 'area_id': '335', 'row_index': 0},
    '風屋': {'name': '風屋', 'area_id': '335', 'row_index': 1},
    # 和歌山県
    '和歌山': {'name': '和歌山', 'area_id': '336', 'row_index': 0},
    '潮岬': {'name': '潮岬', 'area_id': '336', 'row_index': 1},
    # 島根県
    '島根': {'name': '島根', 'area_id': '337', 'row_index': 0},
    '松江': {'name': '松江', 'area_id': '337', 'row_index': 0},
    '浜田': {'name': '浜田', 'area_id': '337', 'row_index': 1},
    # 広島県
    '広島': {'name': '広島', 'area_id': '338', 'row_index': 0},
    '呉': {'name': '呉', 'area_id': '338', 'row_index': 0},
    '福山': {'name': '福山', 'area_id': '338', 'row_index': 0},
    '庄原': {'name': '庄原', 'area_id': '338', 'row_index': 1},
    # 鳥取県
    '鳥取': {'name': '鳥取', 'area_id': '339', 'row_index': 0},
    '米子': {'name': '米子', 'area_id': '339', 'row_index': 1},
    # 岡山県
    '岡山': {'name': '岡山', 'area_id': '340', 'row_index': 0},
    '津山': {'name': '津山', 'area_id': '340', 'row_index': 1},
    # 香川県
    '香川': {'name': '香川', 'area_id': '341', 'row_index': 0},
    '高松': {'name': '高松', 'area_id': '341', 'row_index': 0},
    # 愛媛県
    '愛媛': {'name': '愛媛', 'area_id': '342', 'row_index': 0},
    '中予': {'name': '中予', 'area_id': '342', 'row_index': 0},
    '東予': {'name': '東予', 'area_id': '342', 'row_index': 1},
    '新居浜': {'name': '新居浜', 'area_id': '342', 'row_index': 1},
    '南予': {'name': '南予', 'area_id': '342', 'row_index': 2},
    '宇和島': {'name': '宇和島', 'area_id': '342', 'row_index': 2},
    # 徳島県
    '徳島': {'name': '徳島', 'area_id': '343', 'row_index': 0},
    '池田': {'name': '池田', 'area_id': '343', 'row_index': 0},
    '日和佐': {'name': '日和佐', 'area_id': '343', 'row_index': 0},
    # 高知県
    '高知': {'name': '高知', 'area_id': '344', 'row_index': 0},
    '室戸岬': {'name': '室戸岬', 'area_id': '344', 'row_index': 1},
    # 山口県
    '下関': {'name': '下関', 'area_id': '345', 'row_index': 0},
    '山口': {'name': '山口', 'area_id': '345', 'row_index': 1},
    '柳井': {'name': '柳井', 'area_id': '345', 'row_index': 2},
    '萩': {'name': '萩', 'area_id': '345', 'row_index': 3},
    # 福岡県
    '福岡': {'name': '福岡', 'area_id': '346', 'row_index': 0},
    '北九州': {'name': '北九州', 'area_id': '346', 'row_index': 1},
    '八幡': {'name': '八幡', 'area_id': '346', 'row_index': 1},
    '筑豊': {'name': '筑豊', 'area_id': '346', 'row_index': 2},
    '飯塚': {'name': '飯塚', 'area_id': '346', 'row_index': 2},
    '筑後': {'name': '筑後', 'area_id': '346', 'row_index': 3},
    '久留米': {'name': '久留米', 'area_id': '346', 'row_index': 3},
    # 佐賀県
    '佐賀': {'name': '佐賀', 'area_id': '347', 'row_index': 0},
    '伊万里': {'name': '伊万里', 'area_id': '347', 'row_index': 1},
    # 長崎県
    '長崎': {'name': '長崎', 'area_id': '348', 'row_index': 0},
    '佐世保': {'name': '佐世保', 'area_id': '348', 'row_index': 1},
    '壱岐': {'name': '壱岐', 'area_id': '348', 'row_index': 2},
    '対馬': {'name': '対馬', 'area_id': '348', 'row_index': 2},
    '厳原': {'name': '厳原', 'area_id': '348', 'row_index': 2},
    # 熊本県
    '熊本': {'name': '熊本', 'area_id': '349', 'row_index': 0},
    '阿蘇': {'name': '阿蘇', 'area_id': '349', 'row_index': 1},
    '天草': {'name': '天草', 'area_id': '349', 'row_index': 2},
    '芦北': {'name': '芦北', 'area_id': '349', 'row_index': 2},
    '牛深': {'name': '牛深', 'area_id': '349', 'row_index': 2},
    '球磨': {'name': '球磨', 'area_id': '349', 'row_index': 3},
    '人吉': {'name': '人吉', 'area_id': '349', 'row_index': 3},
    # 大分県
    '大分': {'name': '大分', 'area_id': '350', 'row_index': 0},
    '中津': {'name': '中津', 'area_id': '350', 'row_index': 1},
    '日田': {'name': '日田', 'area_id': '350', 'row_index': 2},
    '佐伯': {'name': '佐伯', 'area_id': '350', 'row_index': 2},
    # 宮崎県
    '宮崎': {'name': '宮崎', 'area_id': '351', 'row_index': 0},
    '油津': {'name': '油津', 'area_id': '351', 'row_index': 0},
    '延岡': {'name': '延岡', 'area_id': '351', 'row_index': 1},
    '都城': {'name': '都城', 'area_id': '351', 'row_index': 2},
    '高千穂': {'name': '高千穂', 'area_id': '351', 'row_index': 2},
    # 鹿児島県
    '鹿児島': {'name': '鹿児島', 'area_id': '352', 'row_index': 0},
    '薩摩': {'name': '薩摩', 'area_id': '352', 'row_index': 0},
    '阿久根': {'name': '阿久根', 'area_id': '352', 'row_index': 0},
    '枕崎': {'name': '枕崎', 'area_id': '352', 'row_index': 0},
    '大隅': {'name': '大隅', 'area_id': '352', 'row_index': 1},
    '鹿屋': {'name': '鹿屋', 'area_id': '352', 'row_index': 1},
    '種子島': {'name': '種子島', 'area_id': '352', 'row_index': 2},
    '屋久島': {'name': '屋久島', 'area_id': '352', 'row_index': 2},
    '奄美': {'name': '奄美', 'area_id': '352', 'row_index': 3},
    # 沖縄県
    '沖縄': {'name': '沖縄', 'area_id': '353', 'row_index': 0},
    '那覇': {'name': '那覇', 'area_id': '353', 'row_index': 0},
    '名護': {'name': '名護', 'area_id': '353', 'row_index': 1},
    '久米島': {'name': '久米島', 'area_id': '353', 'row_index': 2},
    '宮古島': {'name': '宮古島', 'area_id': '355', 'row_index': 0},
    '石垣島': {'name': '石垣島', 'area_id': '356', 'row_index': 0},
}


class WeatherForecast(Command):

    ptn1 = re.compile('^.*(今日|明日|明後日|あさって|あした)[の|も](.+)の天[気候].*$')
    ptn2 = re.compile('^(.+)[の|も](今日|明日|明後日|あさって|あした)[の|も]天[気候].*$')
    ptn3 = re.compile('^.*(今日|明日|明後日|あさって|あした)[の|も]天[気候].*$')
    ptn4 = re.compile('^(.+)[の|も]天[気候].*$')

    def __init__(self, controller):
        super().__init__(controller)
        self.area = None

    def command(self, *txts):
        when, where = self.extract_condition_word(txts[0])
        if not where:
            if self.area:
                where = self.area
            else:
                return
        where = where.strip('県府')

        if when is None:
           when = '今日'
        if when == '今日':
            offset = 0
        elif when in ('明日', 'あした'):
            offset = 1
        elif when in ('明後日', 'あさって'):
            offset = 1

        area_info = AREAS.get(where)
        if not area_info:
            return

        forecast_table = self.dl_forecast_table(area_info['area_id'])
        weather = self.extract_wheather(forecast_table, area_info['row_index'], offset)
        self.area = where

        txt = self.to_text(when, where, weather)
        self.talk(txt)
        

    def extract_condition_word(self, txt):
        m = self.ptn1.match(txt)
        if m:
            return m.group(1), m.group(2)
        m = self.ptn2.match(txt)
        if m:
            return m.group(2), m.group(1)
        m = self.ptn3.match(txt)
        if m:
            return m.group(1), None
        m = self.ptn4.match(txt)
        if m:
            return None, m.group(1)
        return None, None

    def dl_forecast_table(self, area_id):
        url = 'http://www.jma.go.jp/jp/yoho/{}.html'.format(area_id)
        with urlopen(url) as fp:
            html = fp.read()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        return soup.find('table', id='forecasttablefont')


    def extract_wheather(self, forecast_table, row_index=0, date_offset=0):
        wheather_cells = forecast_table.find_all('th', class_='weather')
        target_cell = wheather_cells[row_index * 3 + date_offset]
        wheather = {'wheather': target_cell.find('img').get('title')}

        temperature_cells = forecast_table.find_all('td', class_='temp')
        target_cell = temperature_cells[row_index * 3 + date_offset]
        min_temp_cell = target_cell.find('td', class_='min')
        if min_temp_cell:
            wheather['min'] = min_temp_cell.text.strip()
        min_temp_cell = target_cell.find('td', class_='max')
        if min_temp_cell:
            wheather['max'] = min_temp_cell.text.strip()

        return wheather

    def to_text(self, when, where, weather):
        txt = '気象庁によると、{}の{}の天気は{}'.format(when, where, weather['wheather'])
        if weather.get('min'):
            txt += '、最低気温は' + weather['min'].replace('-', 'マイナス')
        if weather.get('max'):
            txt += '、最高気温は' + weather['max'].replace('-', 'マイナス')
        txt += 'です'
        return txt


if __name__ == '__main__':
    wf = WeatherForecast()
    while True:
        txt = input()
        if not txt:
            break
        wf.command(txt)
