import logging
import os
from datetime import datetime
import requests
import re
import hashlib
import subprocess


def get_day():
    now = datetime.now()
    exp = "%Y.%m.%d"
    return now.strftime(exp)


def get_base_url():
    hostname = "archlinux.dropswitch.net"
    return "http://{0}/archlinux/iso/latest/".format(hostname)


def get_digest(data, name):
    for line in data:
        logging.debug(line)
    return ""

def get_remote_iso_name():
    base_url = get_base_url()
    data = requests.get(base_url).text
    exp = "archlinux-\d{4}\.\d{2}\.\d{2}-dual\.iso"
    p = re.compile(exp)
    m = p.search(data)
    iso_name = m.group(0)
    logging.debug('Remote iso name: ' + iso_name)
    return iso_name

def get_current_iso_name():
    path = '/mnt/isos/'
    files = os.listdir(path)
    for f in files:
        exp = "archlinux-\d{4}\.\d{2}\.\d{2}-dual\.iso"
        p = re.compile(exp)
        match = p.match(f)
        if match is not None:
            logging.debug('Current iso name: ' + f)
            return f
    return ''
            

def download_remote_iso(iso_name):
    base_url = get_base_url()
    r = requests.get(base_url + iso_name)
    path = '/mnt/isos/{0}'.format(iso_name)
    if r.status_code == 200:
        save(r, path)

def save(data, path):
    with open(path, 'wb') as f:
        for chunk in data:
            f.write(chunk)


def get_remote_iso_md5():
    base_url = get_base_url()
    r = requests.get(base_url + 'md5sums.txt')
    if r.status_code == 200:
        content = r.content.decode("utf-8")
        first_line = content.split('\n')[0]
        md5 = first_line.split(' ')[0]
        logging.debug('Remote MD5 Sum: ' + md5)
        return md5

def get_iso_md5(iso_name):
    path = '/mnt/isos/{0}'.format(iso_name)
    with open(path, 'rb') as file:
        data = file.read()
        iso_md5 = hashlib.md5(data).hexdigest()
        logging.debug('{0} MD5 Sum: {1}'.format(iso_name, iso_md5))
        return iso_md5


def delete_current_iso(name):
    mount_path = '/mnt/archiso'
    iso_path = '/mnt/isos/' + name
    is_mounted = os.path.ismount(mount_path)
    if is_mounted:
        logging.debug('Unmounting ' + mount_path)
        subprocess.call(["umount", "/mnt/archiso"])
    logging.debug("Deleting iso: " + name)
    os.remove(iso_path)

def mount_remote_iso(name):
    mount_path = '/mnt/archiso'
    iso_path = '/mnt/isos/' + name
    logging.debug('Mounting iso: ' + name)
    subprocess.call(["mount", iso_path, mount_path])
        

def main():
    logging.basicConfig(level=logging.DEBUG)
    current_iso_name = get_current_iso_name()
    remote_iso_name = get_remote_iso_name()
    if remote_iso_name == current_iso_name: 
        logging.debug('Iso up to date')
    else:
        logging.info('Downloading new iso')
        download_remote_iso(remote_iso_name)
        remote_md5 = get_remote_iso_md5()
        remote_iso_md5 = get_iso_md5(remote_iso_name)
        if remote_iso_md5 == remote_md5:
            logging.debug('MD5 Sums match')
            delete_current_iso(current_iso_name)
            mount_remote_iso(remote_iso_name)
        else:
            logging.warning('MD5 Sums don\' match')



if __name__ == '__main__':
    main()
