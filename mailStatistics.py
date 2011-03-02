#!/bin/Python27
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# Mail Statistics
#---------------------------------------------------------------------------
# USAGE:
#   python mailStatistics.py
#
# FUNCTION:
#   Retrieves all emails from a label on Gmail and generates
#   a statistic on the ocurrence of the words.
#---------------------------------------------------------------------------

from pattern.web import Mail, GMAIL, SUBJECT
import operator
import getpass
import re
import os.path


def encode_utf8(string):
    # Returns the given string as a Python byte string (if possible).
    if isinstance(string, unicode):
        try:
            return string.encode("utf-8")
        except:
            return string
    return str(string)


def mostUsedWordsInFolder(mail, folder, bCaseSensitive):
    if folder not in mail.folders:
        print("ERROR: Folder doesn't exist!")
        return

    print 'Reading ' + str(mail.folders[folder].count) + ' emails from ' + folder

    # Create word count database. A dict where key=word, value=word count
    database = {}

    # List of regular expressions of quote lines (we call quote line the line
    # introducing the quoted text in a reply email).
    # Supported formats:
    #   2011/2/28 Eduardo Cheng <eduardo@cheng.com>
    #   On Mon, Feb 28, 2011 at 12:00, Eduardo Cheng <eduardo@cheng.com> wrote:
    lReQuoteLine = [r"[0-9]{4}\/[0-9]{1,2}\/[0-9]{1,2} [a-zA-Z][ a-zA-Z\-]* \<[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\.[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\>", r"On [A-Z][a-z]{2}, [A-Z][a-z]{2} [0-9]{1,2}, [0-9]{4} at [0-9]{1,2}\:[0-9]{2}, [a-zA-Z][ a-zA-Z\-]* \<[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\.[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\> wrote\:"]

    # Regular expression of word separators
    reSeparator = r"[\s\.\,\;\:\!\?\(\)\<\>\"\'\*\\\/\=\+\~\_\[\]\{\}]+"

    # List of prefixes indicating it is a reply email
    lReplyPrefixes = ['RE:', 'Re:', 'RES:', 'Res:']

    for i in range(mail.folders[folder].count):

        # Create list of words.
        words = []

        print 'Reading mail ' + str(i+1) + ' of ' + str(mail.folders[folder].count)
        message = mail.folders[folder].read(i, attachments=False, cached=False)

        # Email subject
        # (If the email is a reply, do not count the subject as it is a repetition
        #  of the first email's subject)
        lPrefixSplit = message.subject.split(None,1)
        if len(lPrefixSplit[0]) > 0:
            if lPrefixSplit[0] not in lReplyPrefixes:
                words.extend(re.split(reSeparator, message.subject))

        # Email body
        lines = message.body.splitlines()
        # Search for a quote line. Only count words before the first quote line.
        bQuoteLineFound = False
        for line in lines:
            for regexp in lReQuoteLine:
                if re.search(regexp, line):
                    bQuoteLineFound = True
                    break
            if bQuoteLineFound:
                break
            else:
                words.extend(re.split(reSeparator, line))

        # Count words and add them to the database
        countWords(database, words, bCaseSensitive)

    printDatabase(sorted(database.iteritems(), key=operator.itemgetter(1), reverse=True))


def countWords(database, words, bCaseSensitive):

    # List of regular expressions to be filtered from the results
    filterlist = [ r".*\@.*\.com.*" , r"[0-9]*\/[0-9][0-9]?\/[0-9]*", r"https?\:\/\/.*" , r"^\=\?.*" ]

    for word in words:

        # Transform to lower case
        if not bCaseSensitive:
            word = word.lower()

        # Filter according to expressions in "filterlist"
        inFilter = False
        for regexp in filterlist:
            if re.search(regexp, word):
               inFilter = True
               break

        if inFilter:
            continue

        # Ignores words with 3 or less characters
        if len(word) > 3:
            if word in database:
                database[word] += 1
            else:
                database[word] = 1


def printDatabase(database):

    # Increment output[i].txt until a non-existent filename is found
    j = 0
    while True:
        filename = 'output' + str(j) + '.txt'
        if os.path.exists(filename):
            j += 1
        else:
            break

    fileOutput = open(filename, 'w')

    for key, value in database:
        fileOutput.write(encode_utf8(key) + ' -> ' + str(value) + '\n')

    fileOutput.close()


def main():
    username = raw_input('Enter Gmail username: ')
    password = getpass.getpass('Enter Gmail password: ')
    folder = raw_input('Enter Folder name in lower case: ')
    caseSensitive = raw_input('Enter 1 or 0 for case sensitiveness or insensitiveness: ')
    if caseSensitive not in ['0','1']:
        print("ERROR: Enter either 0 or 1!")
        return
    bCaseSensitive = bool(int(caseSensitive))
    gmail = Mail(username, password, service=GMAIL)
    mostUsedWordsInFolder(gmail, folder, bCaseSensitive)


if __name__ == "__main__":
    main()


