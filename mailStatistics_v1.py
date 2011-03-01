from pattern.web import Mail, GMAIL, SUBJECT
import operator
import getpass
import re
import os.path

def mostUsedWordsInFolder(mail, folder, bCaseSensitive):
    if folder not in mail.folders:
        print("ERROR: Folder doesn't exist!")
        return

    print 'Reading ' + str(mail.folders[folder].count) + ' emails from ' + folder

    # Create word count database. A dict where key=word, value=word count
    database = {}

    # Regular expression of the quote line (we call the quote line
    # the line introducing the quoted text in a reply email).
    # Format: Date Name(s) <Email address>
    #reQuoteLine = r".*[0-9][0-9][0-9][0-9]\/[0-9][0-9]?\/[0-9][0-9]?\ [a-zA-Z][\ a-zA-Z\-]*\ <[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9\.\-\_]+\.[a-zA-Z].*>.*"
    reQuoteLine = r".*On\ .*<.*@.*\.com.*>\ wrote.*"    

    # Regular expression of word separators
    reSeparator = r"[\s\.\,\;\:\!\?\(\)\<\>\"\'\*\\\/\=\+\~\_\[\]\{\}]+"
    
    # List of prefixes indicating it is a reply email
    lReplyPrefixes = ['RE:', 'Re:', 'RES:', 'Res:']
    
    for i in range(mail.folders[folder].count):
    
        # Create list of words.
        words = []
        
        print 'Reading mail ' + str(i+1) + ' of ' + str(mail.folders[folder].count)
        message = mail.folders[folder].read(i, attachments=False, cached=True)
        
        # Email subject       
        # (If the email is a reply, do not count the subject as it is a repetition
        #  of the first email's subject)
        lPrefixSplit = message.subject.split(None,1)
        if lPrefixSplit[0] not in lReplyPrefixes:
            words.extend(re.split(reSeparator, message.subject))

        # Email body
        lines = message.body.splitlines()
        for line in lines:
            # Search for a quote line. Only count words before the first quote line.
            if re.search(reQuoteLine, line):
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
        ## Observacao interna: esse IF nao eh eficiente. Temos que verifica-lo toda vez que recomecamos
        ## o FOR. O ideal seria verificar uma vez soh. Mas eh que eu achei facil colocar aqui.
        if not bCaseSensitive:
            word = word.lower()
        
        # Filter according to expressions in "filterlist"
        inFilter = False
        for regexp in filterlist:
            if re.search(regexp, word):
               inFilter = True
               continue

        if inFilter:
            continue

        # Word can become empty after strip
        # Also ignores words with 3 or less characters
        if word != "" and len(word) > 3:            
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
         fileOutput.write(key.encode('utf-8') + ' -> ' + str(value) + '\n')

    fileOutput.close()


def main():
    username = raw_input('Enter Gmail username: ')
    password = getpass.getpass('Enter Gmail password: ')
    folder = raw_input('Enter Folder name: ')
    caseSensitive = raw_input('Enter 1 or 0 for case sensitiveness or insensitiveness: ')
    if caseSensitive not in ['0','1']:
        print("ERROR: Enter either 0 or 1!")
        return
    bCaseSensitive = bool(int(caseSensitive))
    gmail = Mail(username, password, service=GMAIL)
    mostUsedWordsInFolder(gmail, folder, bCaseSensitive)


if __name__ == "__main__":
    main()


