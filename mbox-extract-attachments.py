#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Wending Mai <wdm@ieee.org>"
__license__ = "GNU GPLv3+"
__version__ = 1.0
__date__ = "2016-03-10"

import email
import mailbox
import os
import sys
import logging
import fnmatch
import hashlib
from email.utils import parsedate

BLACKLIST = set(['signature.asc', 'message-footer.txt', 'smime.p7s'])

def extract_date(email):
    date = email.get('Date')
    return parsedate(date)

def extract_attachment(msg, destination, attachment_db):
    if msg.is_multipart():
        logging.error("tried to extract from multipart: %s" % destination)
        return

    attachment_data = msg.get_payload(decode=True)

    attachment_hash = hashlib.sha1(attachment_data).hexdigest()
    if attachment_hash in attachment_db:
        logging.debug("already extracted attachment")
        return
    attachment_db.add(attachment_hash)

    orig_destination = destination
    n = 1
    while os.path.exists(destination):
        destination = orig_destination + "." + str(n)
        n += 1

    try:
        with open(destination, "wb") as sink:
            sink.write(attachment_data)
    except IOError as e:
        logging.error("io error while saving attachment: %s" % str(e))

def wanted(filename):
    if filename in BLACKLIST:
        return False
    #for ext in ['*.doc', '*.docx', '*.odt', '*.pdf', '*.rtf']:
    for ext in ['*.pdf']:
        if fnmatch.fnmatch(filename, ext):
            return True
    return False

def process_message(msg, directory, attachment_db,index):
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename and wanted(filename):
                logging.debug("extract filename: %s" % filename)
                #destination = os.path.join(directory, filename)
                filename_new=str(index)+'.pdf'
                destination = os.path.join(directory,filename_new)
                extract_attachment(part, destination, attachment_db)
            if not filename:
                logging.debug("found message with nameless attachment: %s" % msg['subject'])

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: %s <mbox_file> [directory]" % sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]
    directory = os.path.curdir

    logging.basicConfig(
        filename='attachment-%s.log' % os.path.basename(filename),
        level=logging.DEBUG)

    if not os.path.exists(filename):
        print("file doesn't exist:", filename)
        sys.exit(1)

    if len(sys.argv) == 3:
        directory = sys.argv[2]
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print("Directory doesn't exist:", directory)
            sys.exit(1)

    box = mailbox.mbox(filename)

    sorted_mails = sorted(box, key=extract_date)
    box.update(enumerate(sorted_mails))
    box.flush()

    print("counting messages for %s... " % filename)
    message_count = len(box)
    print("%s contains %s messages" % (filename, message_count))

    attachment_db = set()
    index=0
    for msg in box:
        index+=1
        process_message(msg, directory, attachment_db,index)
    print("extracted %s attachments" % len(attachment_db))

if __name__ == '__main__':
    main()
