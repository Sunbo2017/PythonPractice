import os
import json
import queue
import html
import re
import time
import clickhouse_driver
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from bs4.element import Comment
from urllib import request

q = queue.Queue()
# the path to store html tips
tips_dir = './tips'
# read tip number from this file
tip_num_file = './nums.txt'
# write json result into this file after html parsed
result_json_file = './kb-lenovo.json'

base_url = 'https://datacentersupport.lenovo.com/us/en/solutions/'


def connect_clickhouse():
    ch_host = '10.121.221.19'
    ch_port = '9000'
    ch_db = 'tips'
    ch_user = 'default'
    ch_pwd = ''
    client = clickhouse_driver.Client(host=ch_host, port=ch_port, database=ch_db, user=ch_user, password=ch_pwd)

    return client


def get_content(file_path):
    with open(file_path, 'rb') as content_file:
        content = content_file.read()
    return content


# get info from h2
def get_section_code_content1(bs, name):
    content = ''
    section = bs.find_all('h2', text=name)
    if name == 'Symptom' and len(section) == 0:
        section = bs.find_all('h2', text='Issue')
    if section and len(section) > 0:
        content_list = []
        siblings = section[0].next_siblings
        for sibling in siblings:
            # print(str(sibling))
            if str(sibling) != '\n':
                if isinstance(sibling, Comment):
                    continue
                if sibling.name == 'h2':
                    break
                if sibling.name == 'ul' or sibling.name == 'ol':
                    ul_children = sibling.contents
                    for child in ul_children:
                        if child.name == 'li':
                            content_list.append(str_format(child.text))
                elif isinstance(sibling, NavigableString):
                    content_list.append(str(sibling.strip('\n')))
                else:
                    content_list.append(sibling.text.strip('\n'))
        # reformat
        # content = re.sub(r'\n    \n', '\n\n', content)
        if name == 'Affected configurations':
            return content_list
        content = ' '.join(content_list)
        content = content.replace('\u00a0', ' ').replace('\xa0', '')
        # print(content)
    return content


# get info from table
def get_section_code_content2(bs, name):
    content = ''
    section = bs.find_all('th', text=name)
    if name == 'Symptom' and len(section) == 0:
        section = bs.find_all('th', text='Issue')
    if section and len(section) > 0:
        content_list = []
        siblings = section[0].parent.parent.next_siblings
        for sibling in siblings:
            if str(sibling) != '\n':
                if isinstance(sibling, Comment):
                    continue
                if sibling.name == 'table':
                    break
                if sibling.name == 'ul' or sibling.name == 'ol':
                    ul_children = sibling.contents
                    for child in ul_children:
                        if child.name == 'li':
                            content_list.append(str_format(child.text))
                elif isinstance(sibling, NavigableString):
                    content_list.append(str(sibling.strip('\n')))
                else:
                    content_list.append(sibling.text.strip('\n'))
            # print(str(sibling))
        # reformat
        # content = re.sub(r'\n    \n', '\n\n', content)
        if name == 'Affected configurations':
            return content_list
        content = ' '.join(content_list)
        content = content.replace('\u00a0', ' ').replace('\xa0', '')
    return content


def get_section_table_contents(bs, name):
    result = []
    section = bs.find_all('h2', class_='title', text=name)
    if section and len(section) > 0:
        tds = section[0].parent.parent.parent.next_sibling.find_all('td')
        for td in tds:
            result.append(td.get_text())
    return result


def get_section_paragraph_contents(bs, name):
    result = []
    section = bs.find_all('h3', text=name)
    if section and len(section) > 0:
        ps = section[0].next_sibling.next_sibling.find_all('p')
        for p in ps:
            result.append(p.get_text())
    return result


def get_section_code_content(bs):
    content_dict = {}
    sections = bs.find_all()
    isTable = False
    if sections[0].name == 'table':
        isTable = True
    if sections and len(sections) > 0:
        content_list = []
        h3_key = ''
        # len+1 to get last one field
        for i in range(len(sections)+1):
            if i == len(sections):
                if h3_key in ['affected_configurations', 'affected_firmware', 'affected_brands', 'affected_systems']:
                    content_dict[h3_key] = content_list
                else:
                    content_dict[h3_key] = ' '.join(content_list)
                return content_dict

            section = sections[i]
            if section.name in ['h2', 'h3']:
                if h3_key and content_list:
                    if h3_key in ['affected_configurations',
                                  'affected_firmware',
                                  'affected_brands',
                                  'affected_systems']:
                        content_dict[h3_key] = content_list
                    else:
                        content_dict[h3_key] = ' '.join(content_list)
                h3_key = section.text.lower().strip().replace(' ', '_')
                # some tips use wrong symtom
                if 'symptom' in h3_key or 'symtom' in h3_key:
                    h3_key = 'symptom'
                elif 'firmware' in h3_key:
                    h3_key = 'affected_firmware'
                elif 'affected_systems' in h3_key:
                    h3_key = 'affected_systems'
                elif 'affected_configuration' in h3_key:
                    h3_key = 'affected_configurations'
                content_list = []
            else:
                # content_list.append(section.text)
                if section.name == 'p':
                    # if root section is table, add p
                    if isTable:
                        content_list.append(str_format(section.text))
                    elif section.parent.name != 'td':
                        # print(section.text)
                        # remove \xa0 \n
                        # content_list.append(''.join(str(section.text).split()))
                        content_list.append(str_format(section.text))
                elif section.name == 'table':
                    # print(section.text)
                    # remove \xa0 \n
                    # content_list.append(''.join(str(section.text).split()))
                    content_list.append(str_format(section.text))
                elif section.name == 'ul' or section.name == 'ol' and section.parent.name != 'li':
                    # ul_children = section.contents
                    # for child in ul_children:
                    #     if child.name == 'li':
                    content_list.append(str_format(section.text))
                # if <br/> in <p> will write repeat message,so add: section.parent.name != 'p'
                elif section.name == 'br' and section.previous.string \
                        and section.parent.name not in ['p', 'span', 'li']:
                    # print(section.text)
                    content_list.append(str_format(section.previous.string))

    return content_dict


def str_format(source_str):
    result = source_str.replace('\xa0', '').replace('\'', '').replace('\"', '').replace('\t', '')
    # '  - \w+.+\n    \w.+'
    result = re.sub(r'\n(  - \w[^\n]+)\n    (\w)', '\n\\1 \\2', result)
    result = re.sub(r'^\n', '', result)
    result = re.sub(r'\n\n$', '', result)
    result = re.sub(r'\n\s+\n', '\n\n', result)
    result = re.sub(r' +', ' ', result)
    result = result.replace('\u00a0', ' ')
    return result


def find_repeat_nums():
    num_list = []
    with open('D:\\tips\\tip-nums-new', 'r') as fn:
        for num in fn.readlines():
            num_list.append(num.rstrip('\n'))

    target = open('D:\\tips\\kb-lenovo-new.json', 'a+')
    repeat_num = 0
    with open('D:\\tips\\kb-lenovo.json', 'r') as f:
        line = f.readline()
        while line:
            tip_dict = json.loads(line)
            tip_num = tip_dict.get('tip_number')
            print(tip_num)
            if tip_num in num_list:
                repeat_num += 1
                print('repeat:{}'.format(tip_num))
                target.write(line)
                # target.write('\n')
            line = f.readline()

    print('Finish, repeat count:{}'.format(repeat_num))


def find_new_nums():
    num_list = []
    with open('D:\\tips\\nums.txt', 'r') as fn:
        for num in fn.readlines():
            num = num.rstrip()
            if num not in num_list:
                num_list.append(num)

    target = open('D:\\tips\\tip-nums-new', 'a+')
    new_num = 0
    with open('D:\\tips\\nums.txt', 'r') as f:
        line = f.readline()
        while line:
            tip_num = line.rstrip()
            # print(tip_num)
            if tip_num not in num_list:
                new_num += 1
                print('new:{}'.format(tip_num))
                target.write(tip_num)
                target.write('\n')
            line = f.readline()

    print('Finish, new nums count:{}'.format(new_num))


def parse_ibm_tips():
    # work_dir = 'D:\\ibm_tips3'
    work_dir = './ibm_tips'
    start_time = time.time()
    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            # print('File path：%s\n' % file_path)
            q.put(file_path)

    # target = open('{}\\kb-ibm.json'.format(work_dir), 'w')
    target = open('./kb-ibm.json', 'w')
    # ch_client = connect_clickhouse()
    # rows = []
    tip_doc = {}
    month_dict = {
        'January': '01',
        'February': '02',
        'Match': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }
    while not q.empty():
        file_path = q.get()
        content = get_content(file_path)
        print(file_path)
        # tip_doc['file'] = './ibm_tips/{}'.format(file_path.split('\\')[-1])
        tip_doc['file'] = file_path

        bs_all = BeautifulSoup(content, 'html.parser')

        h1 = bs_all.find('h1')
        if not h1:
            continue
        title = h1.find('span').get_text().replace('\n', '').replace('\xa0', ' ')
        print(title)
        tip_doc['title'] = title

        # source = bs.find('h2', text='Source')
        # if not source:
        #     source = bs.find('h2', text='Sourse')
        # if not source:
        #     source = bs.find('th', text='Source').parent.parent

        tip_number = bs_all.find('h2', text='UID').next_sibling.next_sibling.text
        print(tip_number)
        tip_doc['tip_number'] = tip_number

        modified_date = bs_all.find('strong', text='Modified date:').next_sibling.next_sibling.next_sibling
        date_chars = str(modified_date).strip('\n').strip().split(' ')
        year = date_chars[-1]
        day = date_chars[0]
        month = month_dict[date_chars[1]]
        publish_date = '{}-{}-{}'.format(year, month, day)
        print(publish_date)
        tip_doc['publish_date'] = publish_date

        bs = bs_all.find(name='div', class_='clearfix text-formatted field field--name-field-resolution field--type-text-long field--label-above')
        if not bs:
            bs = bs_all.find(name='div', class_='clearfix text-formatted field field--name-field-content field--type-text-long field--label-above')
        if not bs:
            bs = bs_all.find(name='div', class_='clearfix text-formatted field field--name-field-steps field--type-text-long field--label-above')

        # Symptom
        symptom = get_section_code_content1(bs, 'Symptom')
        if not symptom:
            symptom = get_section_code_content2(bs, 'Symptom')
        print('[Symptom]\n{}'.format(symptom))
        tip_doc['symptom'] = symptom

        # Affected Configuration
        affected_configuration = get_section_code_content1(bs, 'Affected configurations')
        if not affected_configuration:
            affected_configuration = get_section_code_content2(bs, 'Affected configurations')
        print('[Affected Configuration]\n{}'.format(affected_configuration))
        tip_doc['affected_configurations'] = affected_configuration

        affected_types = []
        for ac in affected_configuration:
            index = ac.find('Type')
            if index == -1:
                index = ac.find('type')
            if index > -1:
                # BladeCenter Chassis, Type 7967, any model
                index_c = ac.find(',', index)
                af_type = ac[index+5:index_c]
                affected_types.append(af_type)
        # Affected Types
        if not affected_types:
            affected_types.append('0000')
        print('[Affected Types]\n{}'.format(affected_types))
        tip_doc['affected_types'] = affected_types

        # Workaround
        workaround = get_section_code_content1(bs, 'Workaround')
        if not workaround:
            workaround = get_section_code_content2(bs, 'Workaround')
        print('[Workaround]\n{}'.format(workaround))
        tip_doc['workaround'] = workaround

        # Solution
        solution = get_section_code_content1(bs, 'Solution')
        if not solution:
            solution = get_section_code_content2(bs, 'Solution')
        print('[Solution]\n{}'.format(solution))
        tip_doc['solution'] = solution

        # Additional Information
        additional_information = get_section_code_content1(bs, 'Additional information')
        if not additional_information:
            additional_information = get_section_code_content2(bs, 'Additional information')
        print('[Additional Information]\n{}'.format(additional_information))
        tip_doc['additional_information'] = additional_information

        level = ''
        tip_doc['level'] = level
        tip_type = ''
        tip_doc['tip_type'] = tip_type
        cogent_draft = ''
        tip_doc['cogent_draft'] = cogent_draft
        tip_doc['operating_systems'] = ''

        json_tip = json.dumps(tip_doc)
        # print(json_tip)
        target.write(json_tip)
        target.write('\n')

    #     row = [file_path, tip_number, title, level, symptom, workaround, solution, additional_information,
    #            str(affected_configuration), str(affected_types), cogent_draft, publish_date, tip_type]
    #
    #     rows.append(row)
    #
    # print(len(rows))
    # ch_client.execute('INSERT INTO tips.kb VALUES', rows)

    end_time = time.time()
    print('Elapsed time: ', end_time - start_time)


# parse 406 new lenovo tips
def parse_lenovo_tips_new():
    num_list = []
    with open('./tips/tip-nums-new', 'r') as fn:
    # with open('D:\\tips\\tip-nums-new', 'r') as fn:
        for num in fn.readlines():
            num_list.append(num.rstrip('\n'))
    # work_dir = 'D:\\tips2'
    work_dir = './tips'
    start_time = time.time()
    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            # print('File path：%s\n' % file_path)
            q.put(file_path)

    target = open('./tips/kb-lenovo-new.json', 'w')
    # target = open('D:\\tips2\\kb-lenovo-new.json', 'w')
    # ch_client = connect_clickhouse()
    # rows = []

    while not q.empty():
        file_path = q.get()
        tip_number = file_path.split('/')[-1]
        # tip_number = file_path.split('\\')[-1]
        if tip_number not in num_list:
            continue
        content = get_content(file_path)
        print(file_path)

        bs_wrapper = BeautifulSoup(content, 'html.parser')
        js_objs = bs_wrapper.find_all('script', type='text/javascript')
        if js_objs is None:
            continue

        for js_obj in js_objs:
            jses = js_obj.contents
            if len(jses) <= 0:
                continue

            for js in jses:
                i = js.find('var customData = window.customData || ')
                if i <= 0:
                    continue

                j = js.find('\n', i + 38)
                custom_data = json.loads(js[i + 38:j-1])
                # print(custom_data)
                localization = custom_data.get('localization')
                if not localization:
                    continue

                body = localization.get('body')
                if not body:
                    continue

                bs = BeautifulSoup(html.unescape(body), 'html.parser')
                # print(bs)

                tips_dict = get_section_code_content(bs)
                # print(tips_dict)
                title = localization.get('title')
                tips_dict['title'] = title
                publish_date = localization.get('updated')[:10]
                tips_dict['publish_date'] = publish_date

                tips_dict['tip_number'] = tip_number

                cogent_draft = custom_data.get('attributes').get('AliasId', '')
                tips_dict['cogent_draft'] = cogent_draft
                tips_dict['file'] = file_path
                level = 'Unclassified'
                tips_dict['level'] = level
                tip_type = ''
                tips_dict['tip_type'] = tip_type

                # symptom = tips_dict.get('symptom')
                # workaround = tips_dict.get('workaround')
                # solution = tips_dict.get('solution')
                # additional_information = tips_dict.get('additional_information')

                affected_configurations = tips_dict.get('affected_configurations')
                if not affected_configurations:
                    affected_brands = tips_dict.get('affected_brands', [])
                    if affected_brands:
                        del tips_dict['affected_brands']
                    affected_systems = tips_dict.get('affected_systems', [])
                    if affected_systems:
                        del tips_dict['affected_systems']
                    affected_firmware = tips_dict.get('affected_firmware', [])
                    if affected_firmware:
                        del tips_dict['affected_firmware']
                    affected_configurations = affected_brands + affected_systems + affected_firmware
                tips_dict['affected_configurations'] = affected_configurations

                affected_types = get_affected_types(affected_configurations)
                tips_dict['affected_types'] = affected_types

                json_tip = json.dumps(tips_dict)
                # print(json_tip)
                target.write(json_tip)
                target.write('\n')

    #     row = [file_path, tip_number, title, level, symptom, workaround, solution, additional_information,
    #            str(affected_configuration), str(affected_types), cogent_draft, publish_date, tip_type]
    #
    #     rows.append(row)
    #
    # print(len(rows))
    # ch_client.execute('INSERT INTO tips.kb VALUES', rows)

    end_time = time.time()
    print('Elapsed time: ', end_time - start_time)


def get_affected_types(affected_configurations):
    affected_types = []
    for ac in affected_configurations:
        # ThinkSystem SE350, Type 7D1X, any model
        pattern = re.compile(r'.*Type ([0-9A-Z]{4}).*')
        search_objs = re.findall(pattern, ac)
        if search_objs:
            for obj in search_objs:
                if obj not in affected_types:
                    affected_types.append(obj)

    # Affected Types
    if not affected_types:
        affected_types.append('0000')

    # print(affected_types)
    return affected_types


# get repeat tips:next could to rewrite kb.json
def parse_lenovo_tips_repeat():
    num_list = []
    with open('./tips/tip-nums-repeat', 'r') as fn:
        for num in fn.readlines():
            num_list.append(num.rstrip('\n'))
    # work_dir = 'D:\\tips2'
    work_dir = './tips'
    start_time = time.time()
    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            # print('File path：%s\n' % file_path)
            q.put(file_path)

    target = open('./tips/kb-lenovo-repeat.json', 'w')
    # target = open('D:\\tips2\\kb-lenovo.json', 'w')
    # ch_client = connect_clickhouse()
    # rows = []

    while not q.empty():
        file_path = q.get()
        tip_number = file_path.split('/')[-1]
        # tip_number = file_path.split('\\')[-1]
        if tip_number not in num_list:
            continue

        content = get_content(file_path)
        print(file_path)

        bs_wrapper = BeautifulSoup(content, 'html.parser')
        js_objs = bs_wrapper.find_all('script', type='text/javascript')
        if js_objs is None:
            continue

        for js_obj in js_objs:
            jses = js_obj.contents
            if len(jses) <= 0:
                continue

            for js in jses:
                i = js.find('var customData = window.customData || ')
                if i <= 0:
                    continue

                j = js.find('\n', i + 38)
                custom_data = json.loads(js[i + 38:j-1])
                # print(custom_data)
                localization = custom_data.get('localization')
                if not localization:
                    continue

                body = localization.get('body')
                if not body:
                    continue

                bs = BeautifulSoup(html.unescape(body), 'html.parser')
                # print(bs)

                tips_dict = get_section_code_content(bs)
                # print(tips_dict)
                title = localization.get('title')
                tips_dict['title'] = title
                publish_date = localization.get('updated')[:10]
                tips_dict['publish_date'] = publish_date

                tips_dict['tip_number'] = tip_number

                cogent_draft = custom_data.get('attributes').get('AliasId')
                tips_dict['cogent_draft'] = cogent_draft
                tips_dict['file'] = file_path
                level = 'Unclassified'
                tips_dict['level'] = level
                tip_type = ''
                tips_dict['tip_type'] = tip_type

                # symptom = tips_dict.get('symptom')
                # workaround = tips_dict.get('workaround')
                # solution = tips_dict.get('solution')
                # additional_information = tips_dict.get('additional_information')

                affected_configurations = tips_dict.get('affected_configurations', [])
                # if not affected_configurations:
                affected_brands = tips_dict.get('affected_brands', [])
                if affected_brands:
                    del tips_dict['affected_brands']
                affected_systems = tips_dict.get('affected_systems', [])
                if affected_systems:
                    del tips_dict['affected_systems']
                affected_firmware = tips_dict.get('affected_firmware', [])
                if affected_firmware:
                    del tips_dict['affected_firmware']
                affected_configurations = affected_configurations + affected_brands + affected_systems + affected_firmware
                tips_dict['affected_configurations'] = affected_configurations

                affected_types = get_affected_types(affected_configurations)
                tips_dict['affected_types'] = affected_types

                json_tip = json.dumps(tips_dict)
                # print(json_tip)
                target.write(json_tip)
                target.write('\n')
    #
    #     row = [file_path, tip_number, title, level, symptom, workaround, solution, additional_information,
    #            str(affected_configuration), str(affected_types), cogent_draft, publish_date, tip_type]
    #
    #     rows.append(row)
    #
    # print(len(rows))
    # ch_client.execute('INSERT INTO tips.kb VALUES', rows)

    end_time = time.time()
    print('Elapsed time: ', end_time - start_time)


# merge repeat lenovo tips into kb.json(save into kb-merge.json)
def merge_repeat_tips():
    repeat_tip_dict = {}
    with open('./tips/kb-lenovo-repeat.json', 'r') as fn:
        for line in fn.readlines():
            tip_doc = json.loads(line)
            repeat_tip_dict[tip_doc.get('tip_number')] = tip_doc

    target = open('./tips/kb-merge.json', 'w')
    repeat_num = 0
    num = 0
    with open('./tips/kb.json', 'r') as f:
        line = f.readline()
        while line:
            tip_dict = json.loads(line)
            # rename affected_configuration to affected_configurations
            affected_configurations = tip_dict.get('affected_configuration', [])
            if affected_configurations:
                del tip_dict['affected_configuration']
            tip_dict['affected_configurations'] = affected_configurations

            tip_num = tip_dict.get('tip_number')
            print(tip_num)
            if tip_num in repeat_tip_dict.keys():
                repeat_num += 1
                print('repeat:{}'.format(tip_num))
                lenovo_tip_doc = repeat_tip_dict.get(tip_num)
                symptom = lenovo_tip_doc.get('symptom', '')
                if not symptom:
                    # some tips use wrong field:symtom
                    symptom = lenovo_tip_doc.get('symtom', '')
                tip_dict['symptom'] = symptom
                affected_configurations = lenovo_tip_doc.get('affected_configurations', [])
                if affected_configurations:
                    tip_dict['affected_configurations'] = lenovo_tip_doc.get('affected_configurations', [])
                tip_dict['workaround'] = lenovo_tip_doc.get('workaround', '')
                tip_dict['solution'] = lenovo_tip_doc.get('solution', '')
                tip_dict['additional_information'] = lenovo_tip_doc.get('additional_information', '')

            json_tip = json.dumps(tip_dict)
            target.write(json_tip)
            target.write('\n')
            num += 1
            line = f.readline()

    print('Finish, repeat count:{}'.format(repeat_num))
    print('Finish, all lenovo count:{}'.format(num))


# merge all ibm and lenovo tips(save into kb-all.json)
def merge_all_tips():
    # all_tips = []
    target = open('./kb-all.json', 'a')
    num = 0
    with open('./tips/kb-merge.json', 'r') as fn:
        for line in fn.readlines():
            # tip_doc = json.loads(line)
            # all_tips.append(line)
            target.write(line)
            # target.write('\n')
            num += 1

    with open('./tips/kb-lenovo-new.json', 'r') as fn:
        for line in fn.readlines():
            # tip_doc = json.loads(line)
            # all_tips.append(line)
            target.write(line)
            # target.write('\n')
            num += 1

    with open('./ibm_tips/kb-ibm.json', 'r') as fn:
        for line in fn.readlines():
            # tip_doc = json.loads(line)
            # all_tips.append(line)
            target.write(line)
            # target.write('\n')
            num += 1

    print('Finish, all lenovo and ibm count:{}'.format(num))


# download html and return tips need to parse
def get_tips_queue():
    tq = queue.Queue()
    work_dir = tips_dir
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)
    num_file = tip_num_file
    # html tip number need to download
    num_list = []
    with open(num_file, 'r') as fn:
        for num in fn.readlines():
            num = num.rstrip()
            if num not in num_list:
                num_list.append(num)

    # download html
    download_tips(num_list, work_dir)

    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            if filename in num_list:
                file_path = os.path.join(parent, filename)
                # print('File path：%s\n' % file_path)
                tq.put(file_path)

    return tq


def download_tips(num_list, work_dir):
    for num in num_list:
        url = base_url + num
        html_content = request.urlopen(url).read()
        with open(os.path.join(work_dir, num), "wb") as f:
            f.write(html_content)
            print('{} download successful'.format(num))
    print('all html download successful...')


def parse_lenovo_tips():
    start_time = time.time()

    tq = get_tips_queue()
    json_file = result_json_file
    target = open(json_file, 'w')

    while not tq.empty():
        file_path = tq.get()

        content = get_content(file_path)
        print(file_path)

        bs_wrapper = BeautifulSoup(content, 'html.parser')
        js_objs = bs_wrapper.find_all('script', type='text/javascript')
        if js_objs is None:
            continue

        if '\\' in file_path:
            file_path = file_path.replace('\\', '/')
        print(file_path)
        tip_number = file_path.split('/')[-1]
        # tip_number = file_path[-8:]
        # tip_number = file_path.split('\\')[-1]
        for js_obj in js_objs:
            jses = js_obj.contents
            if len(jses) <= 0:
                continue

            for js in jses:
                i = js.find('var customData = window.customData || ')
                if i <= 0:
                    continue

                j = js.find('\n', i + 38)
                custom_data = json.loads(js[i + 38:j-1])
                # print(custom_data)
                localization = custom_data.get('localization')
                if not localization:
                    continue

                body = localization.get('body')
                if not body:
                    continue

                bs = BeautifulSoup(html.unescape(body), 'html.parser')
                print(bs)

                tips_dict = get_section_code_content(bs)
                # print(tips_dict)
                title = localization.get('title')
                tips_dict['title'] = title
                publish_date = localization.get('updated')[:10]
                tips_dict['publish_date'] = publish_date

                tips_dict['tip_number'] = tip_number

                cogent_draft = custom_data.get('attributes').get('AliasId')
                tips_dict['cogent_draft'] = cogent_draft
                tips_dict['file'] = file_path
                level = 'Unclassified'
                tips_dict['level'] = level
                tip_type = ''
                tips_dict['tip_type'] = tip_type

                # symptom = tips_dict.get('symptom')
                # workaround = tips_dict.get('workaround')
                # solution = tips_dict.get('solution')
                # additional_information = tips_dict.get('additional_information')

                affected_configurations = tips_dict.get('affected_configurations', [])
                # if not affected_configurations:
                affected_brands = tips_dict.get('affected_brands', [])
                if affected_brands:
                    del tips_dict['affected_brands']
                affected_systems = tips_dict.get('affected_systems', [])
                if affected_systems:
                    del tips_dict['affected_systems']
                affected_firmware = tips_dict.get('affected_firmware', [])
                if affected_firmware:
                    del tips_dict['affected_firmware']
                affected_configurations = affected_configurations + affected_brands + affected_systems + affected_firmware
                tips_dict['affected_configurations'] = affected_configurations

                affected_types = get_affected_types(affected_configurations)
                tips_dict['affected_types'] = affected_types

                json_tip = json.dumps(tips_dict)
                # print(json_tip)
                target.write(json_tip)
                target.write('\n')
                print('parse {} successful'.format(tip_number))
    #
    #     row = [file_path, tip_number, title, level, symptom, workaround, solution, additional_information,
    #            str(affected_configuration), str(affected_types), cogent_draft, publish_date, tip_type]
    #
    #     rows.append(row)
    #
    # print(len(rows))
    # ch_client.execute('INSERT INTO tips.kb VALUES', rows)
    target.close()
    end_time = time.time()
    print('Elapsed time: ', end_time - start_time)


def read_tip_number():
    num_list = []
    json_file = 'D:\\workFile\\kb-all_200831.json'
    with open(json_file, "r") as f:
        for line in f.readlines():
            json_obj = json.loads(line)
            tip_number = json_obj['tip_number']
            if tip_number.startswith('HT'):
                print(tip_number)
                if '\\' in tip_number:
                    tip_number = tip_number.split('\\')[0]
                num_list.append(tip_number)

    with open('./nums.txt', "w+") as f:
        for num in num_list:
            f.write(num)
            f.write('\n')


if __name__ == '__main__':
    print('-------------------------------- start parse lenovo tips -------------------------------')

    parse_lenovo_tips()
    # read_tip_number()

    # find_repeat_nums()
    # find_new_nums()

    # parse_ibm_tips()
    # print('------------------------------------------------------start parse new lenovo tips')
    # parse_lenovo_tips_new()
    # print('------------------------------------------------------start parse repeat lenovo tips')
    # parse_lenovo_tips_repeat()
    # print('------------------------------------------------------start merge repeat lenovo tips')
    # merge_repeat_tips()
    # print('------------------------------------------------------start merge all lenovo and ibm tips')
    # merge_all_tips()
    print('--------------------------------------- Finish -----------------------------------------')
