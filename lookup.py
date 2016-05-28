import xml.etree.ElementTree as ET
import collections
import re

COMEDIES = ['All\'s Well That Ends Well',
            'As You Like It',
            'The Comedy of Errors',
            'Love\'s Labour\'s Lost',
            'Measure for Measure',
            'The Merchant of Venice',
            'The Merry Wives of Windsor',
            'A Midsummer Night\'s Dream',
            'Much Ado about Nothing',
            'The Taming of the Shrew',
            'The Tempest',
            'Twelfth Night',
            'Two Gentlemen of Verona',
            'The Winter\'s Tale']

HISTORIES = ['Henry IV, Part I',
            'Henry IV, Part II',
            'Henry V',
            'Henry VI, Part I',
            'Henry VI, Part II',
            'Henry VI, Part III',
            'Henry VIII',
            'King John',
            'Pericles',
            'Richard II',
            'Richard III']

TRAGEDIES = ['Antony and Cleopatra',
            'Coriolanus',
            'Cymbeline',
            'Hamlet',
            'Julius Caesar',
            'King Lear',
            'Macbeth',
            'Othello',
            'Romeo and Juliet',
            'Timon of Athens',
            'Titus Andronicus',
            'Troilus and Cressida']

ABBREVIATIONS = {'Wint.' : 'The Winter\'s Tale', 
                'Meas.' : 'Measure for Measure',
                'LLL' : 'Love\'s Labour\'s Lost',
                'Ado' : 'Much Ado about Nothing',
                'Tw.' : 'Twelfth Night',
                'John' : 'King John',
                'V' : 'UNKNOWN',
                'II' : 'UNKNOWN',
                'III' : 'UNKNOWN',
                'IV' : 'UNKNOWN',
                'Tp.' : 'The Tempest', 
                'R2' : 'Richard II',
                'Mids.' : 'A Midsummer Night\'s Dream',
                'Merch.' : 'The Merchant of Venice',
                'Lr.' : 'King Lear',
                'H6A' : 'Henry VI, Part I',
                'Rom.' : 'Romeo and Juliet',
                'Ant.' : 'Antony and Cleopatra',
                'Wiv.' : 'The Merry Wives of Windsor',
                'R3' : 'Richard III',
                'Shr.' : 'The Taming of the Shrew',
                'Ven.' : 'The Merchant of Venice',
                'Cor.' : 'Coriolanus',
                'Mcb.' : 'Macbeth',
                'H4A' : 'Henry IV, Part I',
                'H8' : 'Henry VIII',
                'H5' : 'Henry V',
                'H4B' : 'Henry IV, Part II',
                'H6B' : 'Henry VI, Part II',
                'H6C' : 'Henry VI, Part III',
                'Tit.' : 'Titus Andronicus', 
                'As' : 'As You Like It',
                'Alls' : 'All\'s Well That Ends Well',
                'Tim.' : 'Timon of Athens',
                'Hml.' : 'Hamlet',
                'Oth.' : 'Othello',
                'Err.' : 'The Comedy of Errors',
                'Gent.' : 'Two Gentlemen of Verona',
                'Cymb.' : 'Cymbeline',
                'Gentl.' : 'Two Gentlemen of Verona',
                'Troil.' : 'Troilus and Cressida'}

MAGENTA = '\033[1;35m'
ENDCOLOR = '\033[0m'

class Location:
    def __init__(self, text):
        arr = re.split(r'[, ]+', text)
        length = len(arr)
        if length == 2: self.unpack(arr[0], linenum=arr[1])
        elif length == 3: self.unpack(arr[0], act=arr[1], linenum=arr[2])
        else: self.unpack(*arr)

    def unpack(self, play=None, act=None, scene=None, linenum=None):
        self.play = ABBREVIATIONS[play]
        #self.play = play # when working with a larger file for not not everything has an abbreviation
        self.act = act
        self.scene = scene
        self.linenum = linenum

    def __repr__(self):
        string = self.play + ':'
        if self.act: string += ' ' + self.act + '.'
        if self.scene: string += ' ' + self.scene + '.'
        if self.linenum: string += ' ' + self.linenum
        """ ## The old representation of the object ##
        string = 'Location(play=' + self.play
        if self.act: string += ', act=' + self.act
        if self.scene: string += ', scene=' + self.scene
        if self.linenum: string += ', linenum=' + self.linenum
        string += ')'
        """
        return string

""" ## I didn't end up using these classes, though I may switch back at some point ##
class Context:
    def __init__(self, play, location, quote):
        self.play = play
        self.location = location
        self.quote = quote

class Definitions:
    def __init__(self, definition):
        self.definition
        self.contexts = set()

    def add_context(self, context):
        self.contexts.add(context)

class Lexicon:
    def __init__(self, play, location, quote):
        self.play = play
        self.location = location
        self.quote = quote

    def add_word(word):
        self.curr_word = word

    def add_definition(definition):
        self.curr_definition = definition
"""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def highlight_word(word, quote):
    word = word.lower()
    result = re.sub(r'--s', MAGENTA + word + 's' + bcolors.ENDC, quote)
    result = re.sub(r'([^A-Za-z])' + word[0].lower() + r'\.([^A-Za-z])', '\g<1>' + MAGENTA + word + bcolors.ENDC + '\g<2>', result)
    return result


def parse():
    tree = ET.parse('small.xml')
    root = tree.getroot()
    lexicon = {}
    for x in root.find('text').find('body').findall('div1'):
        entryFrees = x.findall('entryFree')
        for entryFree in entryFrees:
            key = entryFree.get('key').lower()
            word = entryFree.find('orth').text.strip(',')
            addendum = None
            definition = None
            quote = None
            definitions = []
            for c in entryFree:
                if c.tag == 'cit':
                    quote = '"' + c.find('quote').text.strip(',') + '"'
                    location = Location(c.find('bibl').text)
                    quotes.append((quote, [(addendum,location)]))
                    if c.tail: addendum = c.tail.strip('. ')
                    else: addendum = None
                    #print (highlight_word(word,quote))
                elif c.tag == 'bibl': # another bibliography for same quote as above
                    location = Location(c.text)
                    if not quote: quotes.append(('', [(addendum,location)]))
                    else: quotes[-1][1].append((addendum,location))
                    if c.tail: addendum = c.tail.strip('. ') # addendum is for NEXT quote
                    else: addendum = None
                else: #<lb/>
                    if definition: definitions.append((definition, quotes))
                    quotes = []
                    quote = None
                    definition = c.tail.strip(':')
                    definition = re.sub(r' *[0-9]+\) *', '', definition)
            if definition: definitions.append((definition, quotes))
            lexicon[key] = (word,definitions) # but then how do you search by key...

    print_lexicon(lexicon)
    return lexicon


# a more readable print
def print_lexicon(lexicon):
    print (lexicon)
    for key in lexicon:
        (word,definitions) = lexicon[key]
        print_entry(word, definitions)


def print_entry(word, definitions):
    print (word)    
    for i,definition_quotes in enumerate(definitions):
        n = str(i+1) + ')'
        print (n, definition_quotes[0])
        for quote in definition_quotes[1]:
            addendum = quote[1][0][0]
            if addendum and not addendum == '\n': print ('   ', addendum, highlight_word(word, quote[0]))
            else: print ('   ', highlight_word(word, quote[0]))
            for location in quote[1]:
                print('       ', location[1])


def print_entry_play(word, definitions, play):
    word_printed = False   
    i = 1
    for definition_quotes in definitions:
        def_printed = False
        for quote in definition_quotes[1]:
            quote_printed = False
            for location in quote[1]:
                if location[1].play == play:
                    if not word_printed:
                        print (word)
                        word_printed = True
                    if not def_printed:
                        n = str(i) + ')'
                        print (n, definition_quotes[0])
                        def_printed = True
                        i = i + 1
                    if not quote_printed:
                        addendum = quote[1][0][0]
                        if addendum and not addendum == '\n': print ('   ', addendum, highlight_word(word, quote[0]))
                        else: print ('   ', highlight_word(word, quote[0]))
                        quote_printed = True
                    print('       ', location[1])
    return word_printed


def query(lexicon, key, play=None, act=None, scene=None):
    if key in lexicon:
        (word,definitions) = lexicon[key]
        if play: 
            if print_entry_play(word, definitions, play): return
        else: 
            print_entry(word, definitions)
            return 

    print('Sorry, that query did not yield any results')


def welcome(lexicon):
    print('Welcome to the Shakespeare Lexicon and Quotation Dictionary Parser!')
    word = input('Input the word that you would like to search. Note: currently the program only contains the words agent, cabin, marvellous, pail, saddle, and yesty, so I would recommend searching for one of those. ').lower()
    play = get_play()
    if play: query(lexicon, word, play=play)
    else: query(lexicon, word)


def get_play():
    play_map = create_play_map()
    play = input('If you would like to search a specific play only, please enter the corresponding number listed above. (Otherwise hit enter) ')
    while play: 
        try:
            n = int(play)
            if not n in play_map: 
                play = input('That is not a valid play number, try again: ')
                continue
            play = play_map[n]
            # should support act, scene, line numbers here, but haven't implemented that yet
            break
        except: play = input('That is not a valid play number, try again: ')
    return play


def create_play_map():
    play_num = 1
    play_map = {}
    play_num = print_genre('COMEDIES', COMEDIES, play_num, play_map)
    play_num = print_genre('TRAGEDIES', TRAGEDIES, play_num, play_map)
    print_genre('HISTORIES', HISTORIES, play_num, play_map)
    return play_map


def print_genre(genre, plays, play_num, play_map):
    genre = genre + ':'
    print(genre)
    for p in plays:
        print('\t', play_num, '-', p)
        play_map[play_num] = p
        play_num = play_num + 1
    return play_num


if __name__ == '__main__':
    lexicon = parse()
   # welcome(lexicon)

