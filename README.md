README
------

This program parses the Shakespeare Lexicon and Quotation Dictionary xml file and allows the user to search through it. 

The libraries used are ElementTree to help parse the xml, re, collections for defaultdict, and functools for partial during mapping/filtering. 

There are many classes to facilitate parsing and searching, meant to model the format of the Lexicon. The Lexicon contains entries. There can be multiple entries for the same word, so the Lexicon class stores a map from word to set of Entry. Each Entry has a key (i.e. 'happy1'), word (i.e. 'happy'), and a variety of context-specific definitions. For this I created the Definitions class which stores a list of Definition. This is necessary as a wrapper class because it simplifies the process when parsing the xml of appending information to the most recent definition. The Definition class has the string definition as well as a Quotes that is associated with that definition. The Quotes class is a similar wrapper class to the Definitions class. The Quote class stores a string quote and a list of locations. The Location class stores the play, act, scene, and line number at which the quote occurs. In some cases some of this information is omitted in the lexicon (i.e. we might have a line number but no act). The many classes allow for abstraction of tedious parsing, like that at the end the previous quote there may be a tail that the prefix of the next quote that specifies something about how the definition applies to this quote. For example, 'Used of the organs of the body: "his other agents...'. Similarly, the definitions are numbered, and we need to remove those numbers using re.sub so that a filtered lexicon is not constrained to the numbers in the file. In summary the format is as follows: There is a set of entries for each word, each of which has a set of definitions; There can be multiple quotes per definition, each of which has a variable number of locations.

The Lexicon class and each class it contains has a __str__ method, such that when the lexicon is printed it is done so in a nice user-friendly way that can be output directly to the console for the user.

The classes also each have a 'filter' method which filters the class instance for word, play, and location. When filter is called on a lexicon, it returns a filtered Lexicon object, which means you can just print it to give the user their results. The same is true if you call filter on any subclass -- it will return an filtered instance of the class or None if there were not matches. This decomposition makes it very easy to create custom searches with optional information. Once parsed, this makes interacting with the lexicon completely abstracted from the xml and complex formatting (in stark contrast to my initial implementation that was something like a map of sets of lists of lists of sets of tuples).

If the user enters a play that is not in the lexicon, I pick the play with the closest edit distance and ask if that is the play that they meant. I also ensure that they enter roman numerals for act, and positive integers for scene and line numbers. In the future, I hope to offer multiple forms of input, like being able to enter 'One', 'First', '1' or 'I' for the Act, and many alternative play names, like 'H5' for 'Henry 5' or 'Taming' for 'The Taming of the Shrew'. 

To run the program, type 'python lookup.py'. The program will give you instructions on how to query, it should be fairly straightforward. 

Here are a few queries that will test the program's functionality:
    'dfiajfgrw' as the word (or equivalent) to test a search that does not yield any results.
    'yesty' for word, no play.
    'agent' for word, 'mrure for measure' for play to show spelling correction
    'yesty', 'macbeth', 'iv', '1', '53', '' to test a very specific query
    enter the empty string to all to print the entire lexicon

As the program will tell you when you run it, the lexicon ('small.xml') only contains the words agent, cabin, marvellous, and yesty. After it became clear that figuring out how the 50,000 xml (and its many special cases) are formatted was going to be a nightmare, I figured my efforts for this class were better spent on the code for this app given a parseable xml. Once I figure out how the xml works, this code should only need to be modified to handle new parses, but the underlying data structures and their attributes should not need to be changed (i.e. I might have to modify the LexiconParser methods, but the Lexicon class and the classes it contains shouldn't need to be modified much). 
