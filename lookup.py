import xml.etree.ElementTree as ET
import collections
import re
import functools

FILENAME = 'small.xml'

Genre = collections.namedtuple('Genre', ['genre','plays'])

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

PLAYS = [Genre('COMEDIES', COMEDIES), Genre('HISTORIES', HISTORIES), Genre('TRAGEDIES', TRAGEDIES)]

ALL_PLAYS = COMEDIES + HISTORIES + TRAGEDIES

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

# The location class stores a play, and optional act, scene, and line number
# The is used to store the location at which a certain quote appears
class Location:
    # the location is initialized from a text string that definitely contains a play,
    # and, if it contains only a single other string that is the linenumber,
    # if it has two other strings it is the act and the linenumber, and if it 
    # has three others we can unpack the array into all of the arguments. Note
    # that we cannot use array unpacking for all cases because they are listed in 
    # the file in the opposite order that we need them in
    def __init__(self, text):
        arr = re.split(r'[, ]+', text)
        length = len(arr)
        if length == 2: self.unpack(arr[0], linenum=arr[1])
        elif length == 3: self.unpack(arr[0], act=arr[1], linenum=arr[2])
        else: self.unpack(*arr)

    # since python does not support multiple constructors
    def unpack(self, play=None, act=None, scene=None, linenum=None):
        self.play = ABBREVIATIONS[play]
        self.act = act
        self.scene = scene
        self.linenum = int(linenum)

    def is_match(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        return (self.play == play) and (not act or self.act == act) and (not scene or self.scene == scene) and (not linenum_start or (linenum_end >= self.linenum >= linenum_start))

    # prints the location in a way that will be seen by the user next to the quote 
    def __repr__(self):
        string = self.play + ':'
        if self.act: string += ' ' + self.act + '.'
        if self.scene: string += ' ' + self.scene + '.'
        if self.linenum: string += ' ' + str(self.linenum)
        return string


class Quote:
    """
    A Quote has a quote and a list of locations at which that quote appears 
    """
    def __init__(self, quote, location):
        self.quote = quote
        self.locations = [location]

    def add_location(self, location):
        self.locations.append(location)

    def set_locations(self, locations):
        self.locations = locations

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        filtered_locations = list(filter(functools.partial(Location.is_match, play=play, act=act, scene=scene, linenum_start=linenum_start, linenum_end=linenum_end), self.locations))
        return self.quote_with_locations(filtered_locations) if filtered_locations else None

    def quote_with_locations(self, filtered_locations):
        result = Quote(self.quote, filtered_locations[0])
        result.set_locations(filtered_locations)
        return result

    def __repr__(self):
        return '\n    ' + self.quote + ''.join(map(lambda x: '\n\t' + str(x), self.locations))

class Quotes:
    """
    A Quotes has a list of Quote. It is used as a simpler interface to use the Quote
    methods on the most recent Quote in the list
    """
    def __init__(self, quotes=None):
        if quotes: self.quotes = quotes
        else: self.quotes = []
        self.prefix = None

    def add_quote(self, quote, location, prefix):
        if self.prefix: quote = self.prefix + ' ' + quote
        self.quotes.append(Quote(quote,location))
        self.set_prefix(prefix)

    def add_location(self, location, prefix):
        if len(self.quotes) > 0: self.quotes[-1].add_location(location)
        # some entries only have locations, no quotes
        else: self.add_quote('', location, prefix)
        self.set_prefix(prefix)

    # if the word has a tail, this is the prefix to be printed before the next quote
    def set_prefix(self, prefix):
        if prefix: self.prefix = prefix.strip('. ')
        else: self.prefix = None

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        filtered_quotes = list(filter(lambda x: x is not None, [quote.filter(play, act, scene, linenum_start, linenum_end) for quote in self.quotes]))
        return Quotes(filtered_quotes) if filtered_quotes else None


    def __repr__(self):
        return ''.join(map(lambda x: str(x), self.quotes))
        

class Definition:
    """
    A Definition has a definition string and a Quotes assocated with the definition.
    There are one-liner calls to the Quotes methods for ease of use.
    """
    def __init__(self, definition, quotes=None):
        definition = definition.strip(':')
        definition = re.sub(r' *[0-9]+\) *', '', definition)
        self.definition = definition
        if quotes: self.quotes = quotes
        else: self.quotes = Quotes()

    def add_quote(self, quote, location, prefix):
        self.quotes.add_quote(quote, location, prefix)

    def add_location(self, location, prefix):
        self.quotes.add_location(location, prefix)

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        filtered_quotes = self.quotes.filter(play, act, scene, linenum_start, linenum_end)
        return Definition(self.definition, filtered_quotes) if filtered_quotes else None

    def __repr__(self):
        return str(self.definition) + str(self.quotes)

class Definitions:
    """
    A Definitions has a list of Definition. Simplifies use and creates abstraction
    """
    def __init__(self, definitions=None):
        if definitions: self.definitions = definitions
        else: self.definitions = []

    def add_definition(self, definition):
        self.definitions.append(Definition(definition))

    def add_quote(self, quote, location, prefix):
        self.definitions[-1].add_quote(quote, location, prefix)

    def add_location(self, location, prefix):
        self.definitions[-1].add_location(location, prefix)

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        filtered_definitions = list(filter(lambda x: x is not None, [definition.filter(play, act, scene, linenum_start, linenum_end) for definition in self.definitions]))
        return Definitions(filtered_definitions) if filtered_definitions else None

    def __repr__(self):
        return ''.join(map(lambda x,i: '\n' + str(i+1) + ') ' + str(x), self.definitions, range(len(self.definitions))))

class Entry:
    """
    An Entry stores a key, a word and a Definitions
    """
    def __init__(self, key, word, definitions=None):
        self.key = key
        self.word = word
        if definitions: self.definitions = definitions
        else: self.definitions = Definitions()

    def add_definition(self, definition):
        self.definitions.add_definition(definition)

    def add_quote(self, quote, location, prefix):
        self.definitions.add_quote(Coloring.highlight_word(self.word, quote), location, prefix)

    def add_location(self, location, prefix):
        self.definitions.add_location(location, prefix)

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        filtered_definitions = self.definitions.filter(play, act, scene, linenum_start, linenum_end)
        return Entry(self.key, self.word, filtered_definitions) if filtered_definitions else None

    def __repr__(self):
        return str(self.definitions)


class Lexicon:
    """
    A Lexicon stores a map from a word to a set of Entry. The keys are unique but the words are not, 
    which is why there can be more than one Entry per word. We look things up by word, not key, hence
    the choice of representation.
    """
    def __init__(self):
        self.map = collections.defaultdict(lambda: set()) 
        self.curr_entry = None

    def add_entry(self, key, word):
        #if self.curr_entry: self.map[self.curr_entry.word].add(self.curr_entry)
        self.curr_entry = Entry(key, word)
        self.map[word.lower()].add(self.curr_entry) # pretty sure this should work by reference...

    def add_definition(self, definition):
        self.curr_entry.add_definition(definition)

    def add_quote(self, quote, location, prefix):
        self.curr_entry.add_quote(quote, location, prefix)

    def add_location(self, location, prefix):
        self.curr_entry.add_location(location, prefix)

    def add_entry_object(self, entry):
        self.map[entry.word].add(entry)

    def set_entries(self, word, entries):
        if entries: self.map[word] = entries

    def size(self):
        return len(self.map)

    def filter(self, word=None, play=None, act=None, scene=None, linenum_start=None, linenum_end=None):
        if word:
            word = word.lower()
            if not self.map[word]: return None
            result = Lexicon()
            if play: result.set_entries(word, set(filter(lambda x: x is not None, [entry.filter(play, act, scene, linenum_start, linenum_end) for entry in self.map[word]])))
            else: result.set_entries(word, self.map[word])
            return result if result.size() > 0 else None

        result = Lexicon()
        for word in self.map:
            if play: result.set_entries(word, set(filter(lambda x: x is not None, [entry.filter(play, act, scene, linenum_start, linenum_end) for entry in self.map[word]])))
            else: result.set_entries(word, self.map[word])
        return result if result.size() > 0 else None

    #def filter_entries(self, word, play=None, act=None, scene=None, linenum=None)

    def __repr__(self):
        string = ''
        for word in self.map:
            string += Coloring.bold_word(word[0].upper() + word[1:] + ':')
            entries = self.map[word]
            for entry in entries: string += '\t' + str(entry) + '\n'
        return string


class LexiconParser:
    def __init__(self, filename):
        self.lexicon = Lexicon()
        self.parse_xml(filename)

    def parse_xml(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        for div in root.find('text').find('body').findall('div1'):
            for x in div.findall('entryFree'):
                self.parse_xml_entry(x)
            #map(self.parse_xml_entry, )

    def parse_xml_entry(self, xml_entry):
        key = xml_entry.get('key').lower()
        word = xml_entry.find('orth').text.strip(',')
        self.lexicon.add_entry(key, word)

        for xml_sub_entry in xml_entry:
            self.parse_xml_sub_entry(xml_sub_entry) 
        #map(self.parse_xml_sub_entry, xml_entry)

    def parse_xml_sub_entry(self, xml_sub_entry):
        if xml_sub_entry.tag == 'cit': self.parse_quote(xml_sub_entry) 
        elif xml_sub_entry.tag == 'bibl': self.parse_location(xml_sub_entry)
        else: self.parse_definition(xml_sub_entry)

    def parse_definition(self, xml_sub_entry):
        self.lexicon.add_definition(xml_sub_entry.tail)

    def parse_location(self, xml_sub_entry):
        self.lexicon.add_location(Location(xml_sub_entry.text), xml_sub_entry.tail)

    def parse_quote(self, xml_sub_entry):
        quote = '"' + xml_sub_entry.find('quote').text.strip(',') + '"'
        location = Location(xml_sub_entry.find('bibl').text)
        self.lexicon.add_quote(quote, location, xml_sub_entry.tail)

    def search(self, word=None, play=None, act=None, scene=None, linenum_start=None, linenum_end=None):
        #results = self.lexicon.search(play, act, scene, linenum)
        return self.lexicon.filter(word, play, act, scene, linenum_start, linenum_end)

    def print_lexicon(self):
        print(self.lexicon)


# put this inside the lexicon class? 
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
    word = input('Input the word that you would like to search. Note: currently the program only contains the words agent, cabin, marvellous, and yesty, so I would recommend searching for one of those. ').lower()
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


def closest_play(attempt):
    attempt = attempt.lower()
    distances = [(p, edit_distance(attempt, p.lower())) for p in ALL_PLAYS]
    return min(distances, key=lambda x: x[1])[0]

def edit_distance(str1, str2):
    """
    Based on algorithm for cs124. I tried using the code from the last assignment,
    but it was really slow, perhaps because it was recursive
    """
    num_rows = len(str1)+1
    num_cols = len(str2)+1
    d = [[None] * num_cols for _ in range(num_rows)]#new int[str1.length() + 1][str2.length() + 1];
    for i in range(num_rows): d[i][0] = i;
    for j in range(num_cols): d[0][j] = j;

    for i in range(1,num_rows):
        for j in range(1,num_cols):
            x = d[i-1][j] + 1;
            y = d[i][j-1] + 1;
            z = d[i-1][j-1];
            if str1[i-1] != str2[j-1]: z = z + 2
            d[i][j] = min(min(x, y), z);
    

    #System.out.println("Edit distance: " + str1 + ", " + str2 + " = "  + d[str1.length()][str2.length()]);
    return d[-1][-1];

class Coloring:
    TRASH_COLOR = '\033[33m'
    MAGENTA = '\033[35m'
    MAGENTA_BOLD = '\033[1;35m'
    ENDCOLOR = '\033[0m'

    def highlight_word(word, quote):
        word = word.lower()
        result = re.sub(r'--s', Coloring.MAGENTA + word + 's' + Coloring.ENDCOLOR, quote)
        result = re.sub(r'([^A-Za-z])' + word[0].lower() + r'\.([^A-Za-z])', '\g<1>' + Coloring.MAGENTA + word + Coloring.ENDCOLOR + '\g<2>', result)
        return result

    def bold_word(word):
        return Coloring.color_word(word, Coloring.MAGENTA_BOLD)

    def color_word(word, color):
        return color + word + Coloring.ENDCOLOR

    def get_input(prompt='Query? ', color=TRASH_COLOR):
        return input(Coloring.color_word(prompt, color))

if __name__ == '__main__':
    # list to list plays with indices or print to print the entire lexicon
    lexicon_parser = LexiconParser(FILENAME)

    print(lexicon_parser.search('Agent', 'Macbeth', 'III'))
    print(lexicon_parser.search())
    print(lexicon_parser.search(play='Macbeth'))
    print(lexicon_parser.search(play='Macbeth', linenum_start=20, linenum_end=60))
    #print(Coloring.get_input())
    #print(closest_play('tming of the shrew'))
   # welcome(lexicon)

