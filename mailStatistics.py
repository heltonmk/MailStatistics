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
import mimify


def encode_utf8(string):
    # Returns the given string as a Python byte string (if possible).
    if isinstance(string, unicode):
        try:
            return string.encode("utf-8")
        except:
            return string
    return str(string)


def mostUsedWordsInFolder(mail, folder, isCaseSensitive):
    if folder not in mail.folders:
        print("ERROR: Folder doesn't exist!")
        return

    print 'Reading ' + str(mail.folders[folder].count) + ' emails from ' + folder

    # Create word count database. A dict where key=word, value=word count
    database = {}

    # List of prefixes indicating it is a reply message
    replyPrefixes = ['RE:', 'Re:', 'RES:', 'Res:']

    # Create list of identifiers of reply lines (we call reply line
    # the line introducing the quoted text in a reply message)
    replyLineIdentifiers = []

    # List of regular expressions to be filtered from the results
    filterlist = [r"[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\.[a-zA-Z]+", r"[0-9]*\/[0-9][0-9]?\/[0-9]*", r"https?\:\/\/.*"]
    subj_filterlist = [r"[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\.[a-zA-Z]+", r"[0-9]*\/[0-9][0-9]?\/[0-9]*", r"https?\:\/\/.*", r"\[.+\]"]

    # Regular expression of word separators
    separators = r"[\s\.\,\;\:\!\?\(\)\<\>\"\'\*\\\/\=\+\~\_\[\]\{\}]+"

    for i in range(mail.folders[folder].count):

        # Create list of words.
        words = []

        print 'Reading mail ' + str(i+1) + ' of ' + str(mail.folders[folder].count)

        # Read old messages first
        j = mail.folders[folder].count - i - 1
        message = mail.folders[folder].read(j, attachments=False, cached=False)

        #---- Email subject ----

        # Headers that contain non-ASCII data use the MIME encoded-word syntax
        # mimify.mime_decode_header outputs only latin1 charset, encode to utf-8 to keep coherence
        subject = message.subject
        try:
            subject = mimify.mime_decode_header(subject).encode("utf-8")
        except UnicodeDecodeError:
            pass

        # Check if it is a reply message. If so, do not count the subject
        # as it is a repetition of the first message's subject.

        isReply = False
        subjectPrefix = subject.split(None,1)
        if subjectPrefix != []:
            if subjectPrefix[0] in replyPrefixes:
                isReply = True
        if not isReply:
            subjectWords = subject.split()
            for word in subjectWords:
                words = splitAndAddWord(word, subj_filterlist, separators, words)

        #---- Email body ----

        if isReply:
            # Search for a reply line. Only count words before the first reply line.
            lines = message.body.splitlines()
            replyLineFound = False
            for line in lines:
                for s in replyLineIdentifiers:
                    if re.search(s, line):
                        replyLineFound = True
                        break
                if replyLineFound:
                    break
                else:
                    bodyWords = line.split()
                    for word in bodyWords:
                        words = splitAndAddWord(word, filterlist, separators, words)
        else:
            bodyWords = message.body.split()
            for word in bodyWords:
                words = splitAndAddWord(word, filterlist, separators, words)

        # Count words and add them to the database
        countWords(database, words, isCaseSensitive)

        # Update the reply line identifiers by adding the author's name and email address
        replyLineIdentifiers = updateReplyLineIdentifiers(replyLineIdentifiers, message, isReply)

    printDatabase(sorted(database.iteritems(), key=operator.itemgetter(1), reverse=True))
    printHTMLChart(sorted(database.iteritems(), key=operator.itemgetter(1), reverse=True))


def splitAndAddWord(word, filters, separators, wordlist):

    # If the word matches a filter, do not add it
    inFilter = False
    for regexp in filters:
        if re.search(regexp, word):
            inFilter = True
            break
    if not inFilter:
        # Split word and add the resulting words to the word list
        wordlist.extend(re.split(separators, word))
    return wordlist


def updateReplyLineIdentifiers(list, message, isReply):

    # Get author's name and email address
    authorIdentity = message.author
    pos = authorIdentity.find(' <')
    authorName = authorIdentity[0:pos]
    authorEmail = message.email_address

    # Update the list of identifiers for the next message
    if isReply:
        list.append(authorName)
        list.append(authorEmail)
    else:
        list = [authorName, authorEmail]
    return list


def countWords(database, words, isCaseSensitive):

    for word in words:

        # Transform to lower case
        if not isCaseSensitive:
            word = word.lower()

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


def printHTMLChart(database):

    # Increment output[i].txt until a non-existent filename is found
    j = 0
    while True:
        filename = 'page' + str(j) + '.html'
        if os.path.exists(filename):
            j += 1
        else:
            break

    fileOutput = open(filename, 'w')

    keys = ""
    values = ""

    count = 0
    for key, value in database:
        keys += '"' + encode_utf8(key) + '", '
        values += str(value) + ", "
        count += 1
        if count >= 10:
            break

    keys = keys[:-2]
    values = values[:-2]
    
    fileOutput.write('')
    fileOutput.write("""<!DOCTYPE html>
                            <html>
                        <head>
                            <title>AwesomeChartJS demo</title>
                            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                            <script type="application/javascript" src="awesomechart.js"> </script>
                        </head>
                        <body>

                            <div class="charts_container">
                                <div class="chart_container">
                                    <canvas id="chartCanvas1" width="960" height="1000">
                                        Your web-browser does not support the HTML 5 canvas element.
                                    </canvas>
                                </div>
                            </div>
                            <script type="application/javascript">
                                var chart1 = new AwesomeChart("chartCanvas1");
                                chart1.chartType = "horizontal bars";
                                chart1.title = "Top 10 words";""");

    fileOutput.write('chart1.data = [' + values + '];')
    fileOutput.write('chart1.labels = [' + keys + '];')

    fileOutput.write("""           chart1.randomColors = true;
                                chart1.draw();
                            </script>
                        </body>
                    </html>""")

    fileOutput.close()


def main():
    username = raw_input('Enter Gmail username: ')
    password = getpass.getpass('Enter Gmail password: ')
    folder = raw_input('Enter Folder name: ')
    folder = folder.lower()
    caseSensitive = raw_input('Enter 1 or 0 for case sensitiveness or insensitiveness: ')
    if caseSensitive not in ['0','1']:
        print("ERROR: Enter either 0 or 1!")
        return
    isCaseSensitive = bool(int(caseSensitive))
    gmail = Mail(username, password, service=GMAIL)
    mostUsedWordsInFolder(gmail, folder, isCaseSensitive)


if __name__ == "__main__":
    main()

    
