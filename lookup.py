import xml.etree.ElementTree as ET
import collections
import re
import functools

"""
This is a user-interactive program that parses the Shakespeare Lexicon and Quotation 
Dictionary and allows the user to search it.
"""

FILENAME = 'small.xml'

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


class Location:
    """ The location class stores a play, and optional act, scene, and line number.
    It is used to store the location at which a certain quote appears. 
    """

    def __init__(self, text):
        """ The location is initialized from a text string that definitely contains a play,
        and, if it contains only a single other string that is the linenumber,
        if it has two other strings it is the act and the linenumber, and if it 
        has three others we can unpack the array into all of the arguments. Note
        that we cannot use array unpacking for all cases because they are listed in 
        the file in the opposite order that we need them in
        """
        arr = re.split(r'[, ]+', text)
        length = len(arr)
        if length == 2: self.unpack(arr[0], linenum=arr[1])
        elif length == 3: self.unpack(arr[0], act=arr[1], linenum=arr[2])
        else: self.unpack(*arr)


    def unpack(self, play=None, act=None, scene=None, linenum=None):
        """ Since python does not support multiple constructors """
        self.play = ABBREVIATIONS[play]
        self.act = act
        self.scene = int(scene) if scene else scene
        self.linenum = int(linenum) if linenum else linenum

    def is_match(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        """ If the given location matches this location """
        return (self.play == play) and (not act or self.act == act) and (not scene or self.scene == scene) and (not linenum_start or (linenum_end >= self.linenum >= linenum_start))

    def __str__(self):
        """ Prints the location in a way that will be seen by the user next to the quote """
        string = self.play + ':'
        if self.act: string += ' ' + self.act + '.'
        if self.scene: string += ' ' + str(self.scene) + '.'
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
        """ Returns this quote with the list of locations that match the given 
        location if there is at least one match, otherwise None """
        filtered_locations = list(filter(functools.partial(Location.is_match, play=play, act=act, scene=scene, linenum_start=linenum_start, linenum_end=linenum_end), self.locations))
        return self.quote_with_locations(filtered_locations) if filtered_locations else None

    def quote_with_locations(self, filtered_locations):
        """ Since python does not support multiple constructors """
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
   
    def set_prefix(self, prefix):
        """ if the word has a tail, this is the prefix to be printed before the next quote """
        if prefix: self.prefix = prefix.strip('. ')
        else: self.prefix = None

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        """ Returns this Quotes with each Quote filtered, if any of them have a 
        location that matches, otherwise None """
        filtered_quotes = list(filter(lambda x: x is not None, [quote.filter(play, act, scene, linenum_start, linenum_end) for quote in self.quotes]))
        return Quotes(filtered_quotes) if filtered_quotes else None

    def __str__(self):
        return ''.join(map(str, self.quotes))
        

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

    def __str__(self):
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

    def __str__(self):
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
        self.definitions.add_quote(TextManipulation.highlight_word(self.word, quote), location, prefix)

    def add_location(self, location, prefix):
        self.definitions.add_location(location, prefix)

    def filter(self, play, act=None, scene=None, linenum_start=None, linenum_end=None):
        filtered_definitions = self.definitions.filter(play, act, scene, linenum_start, linenum_end)
        return Entry(self.key, self.word, filtered_definitions) if filtered_definitions else None

    def __str__(self):
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
        self.curr_entry = Entry(key, word)
        self.map[word.lower()].add(self.curr_entry) 

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

    def filter(self, word=None, play=None, act=None, scene=None, linenum_start=None, linenum_end=None):
        """
        If the user specified a word, return a filtered lexicon for only that word, otherwise filter
        for location on all words.
        """
        result = Lexicon()
        if word:
            word = word.lower()
            if not self.map[word]: return None
            self.filter_entries(word, result, play, act, scene, linenum_start, linenum_end)
        else: 
            for word in self.map: self.filter_entries(word, result, play, act, scene, linenum_start, linenum_end)
        return result if len(result) > 0 else None

    def filter_entries(self, word, result, play=None, act=None, scene=None, linenum_start=None, linenum_end=None):
        if play: result.set_entries(word, set(filter(lambda x: x is not None, [entry.filter(play, act, scene, linenum_start, linenum_end) for entry in self.map[word]])))
        else: result.set_entries(word, self.map[word])

    def __len__(self):
        return len(self.map)

    def __str__(self):
        return ''.join(TextManipulation.bold_word(word[0].upper() + word[1:] + ':') + ''.join('\t' + str(entry) + '\n' for entry in self.map[word]) for word in self.map)


class LexiconParser:
    """ 
    The LexiconParser class takes in a filename and parses that xml file into a Lexicon object.
    """

    def __init__(self, filename):
        self.lexicon = Lexicon()
        self.parse_xml(filename)

    def parse_xml(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        # map wasn't working here...
        for div in root.find('text').find('body').findall('div1'):
            for x in div.findall('entryFree'):
                self.parse_xml_entry(x)

    def parse_xml_entry(self, xml_entry):
        key = xml_entry.get('key').lower()
        word = xml_entry.find('orth').text.strip(',')
        self.lexicon.add_entry(key, word)

        # I tried to use map but it didn't work...
        for xml_sub_entry in xml_entry:
            self.parse_xml_sub_entry(xml_sub_entry) 
        
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
        return self.lexicon.filter(word, play, act, scene, linenum_start, linenum_end)

    def print_lexicon(self):
        print(self.lexicon)


class InputCheck:
    """
    This class ensures we only manipulate correctly formatted user input. 
    """

    def get_roman_numeral(prompt):
        """
        Returns the desired input in roman numeral form.
        None of Shakespeare's plays have enough acts for a roman numeral > 5
        """
        response = TextManipulation.get_input(prompt)
        while response:
            if all(map(lambda x: x == 'i' or x == 'v', response.lower())): return response.upper()
            response = TextManipulation.get_input('Please enter a valid roman numeral: ')

    def get_pos_integer(prompt):
        """ 
        Returns the desired input in integer form.
        """
        response = TextManipulation.get_input(prompt)
        while response:
            try: 
                response = int(response)
                if response > 0: return response
            except: pass
            response = TextManipulation.get_input('Please enter a positive integer: ')

    def get_play():
        """
        Returns a valid play or the empty string according to user input.
        """
        play = TextManipulation.capitalize_first_letter(TextManipulation.get_input('Play? '))
        while play and not (play in ALL_PLAYS):
            closest = InputCheck.closest_play(play)
            response = TextManipulation.get_input('Did you mean ' + closest + '? (y/n) ').lower()
            if response and response[0] == 'y': return closest
            play = TextManipulation.capitalize_first_letter(TextManipulation.get_input('Play? '))
        return play

    def closest_play(attempt):
        """ 
        Returns the play with minimum edit distance to the attempt string
        """
        attempt = attempt.lower()
        distances = [(p, InputCheck.edit_distance(attempt, p.lower())) for p in ALL_PLAYS]
        return min(distances, key=lambda x: x[1])[0]

    def edit_distance(str1, str2):
        """
        Based on algorithm for cs124. I tried using the code from the last assignment,
        but it was really slow, perhaps because it was recursive.
        """
        num_rows = len(str1)+1
        num_cols = len(str2)+1
        d = [[None] * num_cols for _ in range(num_rows)]
        for i in range(num_rows): d[i][0] = i;
        for j in range(num_cols): d[0][j] = j;

        for i in range(1,num_rows):
            for j in range(1,num_cols):
                x = d[i-1][j] + 1;
                y = d[i][j-1] + 1;
                z = d[i-1][j-1];
                if str1[i-1] != str2[j-1]: z = z + 2
                d[i][j] = min(min(x, y), z);
        
        return d[-1][-1];


class TextManipulation:
    """
    The text manipulation class has methods that modify text to either have a specific 
    coloring or a specific capitalization pattern. It is not necessary to create an 
    instance of this class as it does not store information, so all fields 
    and methods are static.
    """

    TRASH_COLOR = '\033[33m'
    MAGENTA = '\033[35m'
    MAGENTA_BOLD = '\033[1;35m'
    ENDCOLOR = '\033[0m'

    def highlight_word(word, quote):
        """
        This method takes in a quote and the word for which the quote is giving context. 
        In the quote the word is substituted by '--s 'or '[word[0]]\.' (-- that is first-letter period).
        Using re we replace those fillers with the actual word, and highlight it in magenta.
        """
        word = word.lower()
        result = re.sub(r'--s', TextManipulation.MAGENTA + word + 's' + TextManipulation.ENDCOLOR, quote)
        result = re.sub(r'([^A-Za-z])' + word[0].lower() + r'\.([^A-Za-z])', '\g<1>' + TextManipulation.MAGENTA + word + TextManipulation.ENDCOLOR + '\g<2>', result)
        return result

    def bold_word(word):
        """ Bolds the given word in magenta """
        return TextManipulation.color_word(word, TextManipulation.MAGENTA_BOLD)

    def color_word(word, color):
        """ Colors a word with the given color """
        return color + word + TextManipulation.ENDCOLOR

    def get_input(prompt='Query? ', color=TRASH_COLOR):
        """ Gets input from the user in a specific color, with a default prompt and color """
        return input(TextManipulation.color_word(prompt, color))

    def capitalize_first_letter(word):
        """ Returns the input string with the first letter of each word capitalized and the rest lowercase """
        return ' '.join(map(lambda x: x[0].upper() + x[1:].lower(), word.split()))


class Query:
    """ This class deals with getting queries from the user and returning results from
    the given lexicon parser.
    """

    def __init__(self, lexicon_parser):
        """ On initialization, asks the user for queries. """
        self.lexicon_parser = lexicon_parser
        self.query()

    def query(self):
        """ While the user would like to continue searching, gets queries from the 
        user, searches the parser, and prints the results if there are any, otherwise 
        prints that there were not matches.
        """
        while True:
            result = self.lexicon_parser.search(*self.get_query())
            print(result if result else 'Sorry, your search did not yield any results.\n')
            if not self.another_query(): break
        print('\nBye! :)')

    def another_query(self):
        """ Continues to prompt the user for a yes or no answer until the user decides
        whether or not they would like to search again. """
        while True:
            response = TextManipulation.get_input('Query again? (y/n) ').lower()
            if not response: continue
            if response[0] == 'n': return False
            if response[0] == 'y': return True

    def get_query(self):
        """ Get and returns a query from the user. The query can contain a word, 
        and/or play. If it contains a play, it may also contain any combination of
        act, scene, and line number range.
        """
        word = TextManipulation.get_input('Word? ')
        play = InputCheck.get_play()
        act, scene, linenum_start, linenum_end = None, None, None, None
        # if they entered a play, they can get more specific
        if play:
            act = InputCheck.get_roman_numeral('Act? ')
            scene = InputCheck.get_pos_integer('Scene? ')
            linenum_start = InputCheck.get_pos_integer('Starting line number? ')
            # only want to ask for an ending line number if they entered a starting 
            # line number. If the enter only a starting line number, they are querying
            # that line only.
            if linenum_start: 
                linenum_end = InputCheck.get_pos_integer('Ending line number? ')
                if not linenum_end: linenum_end = linenum_start
        return (word, play, act, scene, linenum_start, linenum_end)


def welcome():
    """ Prints a welcome message welcoming the user to the progam. Gives information about the program and 
    how to use it. 
    """
    print()
    print('Welcome to the Shakespeare Lexicon and Quotation Dictionary Parser!')
    print('You will be prompted for a word, a play, an act, a scene, and a range of line numbers.')
    print('Please enter the act as a roman numeral and the scene and line numbers as positive integers.')
    print('To omit any search options, click enter.')
    print('If you do not enter a play, you will not be prompted for the rest of the options.')
    print('If you enter only a starting line number and not a range, you will query only that line.')
    print('You can enter location queries without a word, and you can query a word without specifying a play.')
    print('Note: currently the the words in the lexicon are agent, cabin, marvellous, and yesty.')
    print()


if __name__ == '__main__':
    """ When run, the program parses the lexicon, welcomes the user, and allows the user to query.
    In the future there will likely be more menu options, like being able to type "list plays" to list all plays
    or "help" for some helpful information. 
    """
    lexicon_parser = LexiconParser(FILENAME)
    welcome()
    Query(lexicon_parser)

