#!/usr/bin/env python3
import argparse
import os
import sys
import datetime
import csv
import shutil
from pathlib import Path


parse = argparse.ArgumentParser(description="Инструмент для создания резервной копии директории/директорий с файлами и "
                                            "ведением журнала событий архивирования")
parse.add_argument('--directory', action='store', required=True, help="Путь до директории/директорий для архивации")
parse.add_argument('--output', action='store', required=True, help="Путь до директории для архива")
parse.add_argument('-j', '--journal', action='store', default='journal.csv', help="Путь до файла журнала (по умолчанию "
                                                                                  "файл журнала journal.csv создается в"
                                                                                  " директории запуска инструмента "
                                                                                  "архивации)")
parse.add_argument('-a', '--archive', action='store', default='gztar', help="Формат архива gztar, zip, bztar2,"
                                                                            " tar, xztar (по умолчанию формат gztar)")
key = vars(parse.parse_args())


source_dir = os.path.abspath(key.get('directory'))
target_dir = os.path.abspath(key.get('output'))
j_file = os.path.join(key.get('journal'))
bkp_type = key.get('archive')
daytime = datetime.datetime.utcnow()
arch_check = False
status = 'fail'
error = ''

for i in range(len(shutil.get_archive_formats())):
    if shutil.get_archive_formats()[i][0] == bkp_type:
        arch_check = True

if (os.path.exists(source_dir)) and (os.path.exists(target_dir)) and arch_check:
    arch_name = os.path.basename(source_dir) + '_' + daytime.strftime("%Y-%m-%d_%H:%M:%S")
    try:
        shutil.make_archive(target_dir + '/' + arch_name, bkp_type, str(Path(source_dir).parents[0]),
                            os.path.basename(source_dir))
        status = 'success'
        if bkp_type == 'xztar':
            bkp_type = 'tar.xz'
        elif bkp_type == 'bztar2':
            bkp_type = 'tar.bz2'
        elif bkp_type == 'gztar':
            bkp_type = 'tar.gz'
        sys.stdout.write(target_dir + '/' + arch_name + '.' + bkp_type + '\n')
    except OSError as err:
        error = err
else:
    if ~(os.path.exists(source_dir)) or ~(os.path.exists(target_dir)) or ~arch_check:
        sys.stderr.write('Директория/директории не существует или формат архива указан некорректно')
if error != '':
    sys.stderr.write(str(error) + '\n')
try:
    if os.path.isfile(j_file):
        with open(j_file, mode='a') as csv_file:
            fieldnames = ['pathFrom', 'pathTarget', 'archFormat', 'DateTime', 'Status']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({'pathFrom': source_dir, 'pathTarget': target_dir, 'archFormat': bkp_type,
                             'DateTime': daytime, 'Status': status})
    else:
        with open(j_file, mode='w') as csv_file:
            fieldnames = ['pathFrom', 'pathTarget', 'archFormat', 'DateTime', 'Status']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'pathFrom': source_dir, 'pathTarget': target_dir, 'archFormat': bkp_type,
                             'DateTime': daytime, 'Status': status})
except ValueError:
    pass
