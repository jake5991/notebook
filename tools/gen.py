import os
import sys
import re
import platform
import tempfile as temp
import random
import markdown

version = "v0.1"

usageinfo =  \
"""
    Usage: gen.py /path/to/dir/containing/notes/
    \t Read more at http://github.com/jake5991/notebook \n

"""

class expression:
    BOOK_INFO = re.compile('<book.+>')
    LICENCE_INFO = re.compile('.*<licence .+/>')
    COLOPHON = re.compile('.*<colophon.+>')
    UNKNOWN = re.compile('.*<.+>.*')
    ABOUT_DIR = re.compile('.*<about.+/>.*')
    WORD = re.compile('.*<word>.+</word>.*')
    FILE = re.compile('.*<file.+/>.*')

class config:
    path = ''
    aboutfiles = []
    metadata = {'title': '', 'colophon': '', 'extra': '', 'licence': '', 'licence-url': '', 'ver': ''}


def dictFromLine(line):
    pairs = []
    ValueString = re.findall('[a-z]*=".+"', line)
    Seperate = re.split('"\s', ValueString[0])
    for i in Seperate:
        pairs.append(i.replace("\"","").split('='))

    return dict(pairs)

def main():
    try:
        prelims = open(config.path + "prelims.xml", 'r')
    except:
        abort("File Error")
    
    print version + " Checked path \t [ OK ]"

    for line in prelims:
        if (expression.BOOK_INFO.match(line)):
            xml = dictFromLine(line)
            config.metadata['title'] = xml['title']
        elif (expression.LICENCE_INFO.match(line)):
            xml = dictFromLine(line)
            config.metadata['licence-url'] = xml['url']
            config.metadata['licence'] = xml['name']
        elif (expression.COLOPHON.match(line)):
            xml = dictFromLine(line)
            config.metadata['ver'] = xml['version']
        else:
            if not (expression.UNKNOWN.match(line)):
                config.metadata['colophon'] = config.metadata['colophon'] + line.lstrip()

    prelims.close()

    for root, dirs, files in os.walk(config.path):
        for filename in files:
            if (filename.endswith('about.xml')):
                config.aboutfiles.append(root + "/" + filename)
	
    tmp = open('../out/temp.tmp', 'w')
    for path in config.aboutfiles:
        file = open(path, 'r')
        keywords = []
        filelist = []
        topic = ''
        directory = os.path.dirname(path) + "/"
        tmp = open('../out/temp.tmp', 'a')
        for line in file:
            if (expression.ABOUT_DIR.match(line)):
                try:
                    xml = dictFromLine(line)
                    topic = xml['topic'].strip()
                except:
                    abort("XML Error")
            elif (expression.WORD.match(line)):
                keywords.append(line.replace('<word>', '').replace('</word>', '').strip())
            elif (expression.FILE.match(line)):
                try:
                    xml = dictFromLine(line)
                    filelist.append(directory + xml['path'].strip())
                except:
                    abort("XML Error")
        #tmp.write(config)

			
        if keywords:
            tmp.write('<h3> Keywords </h3>')

        for keyword in keywords:
            tmp.write('<ul>')
            tmp.write('<li>'+ keyword + '</li>')
            tmp.write('</ul>')

        for file in filelist:
            tmp.write('<div id="' + os.path.basename(file).strip().replace('.md', '') + '">'  + '\n')
            tmp.write('<h2>' + os.path.basename(file).strip().replace('.md', '').replace('_', ' ') + '</h2>'  + '\n')
            read = open(file, 'r')
            text = read.read()
            tmp.write(markdown.markdown(text))

	tmp.close()
	content = open('../out/temp.tmp', 'r').read()

	for keyword in keywords:
		content = content.replace(keyword, '<strong>' + keyword + '</strong>')
		
	final = open('../out/' + config.metadata['title'] + '.html', 'w')
	final.write(content)
	final.close()




def isDir(path):
    return os.path.isdir(path)

def abort(message):
    print message
    sys.exit()

config = config()

if (len(sys.argv) == 2):
    if (isDir(sys.argv[1])):
        config.path = sys.argv[1]
        main()
else:
    print usageinfo
