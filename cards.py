# TITLE:  cards.py
# AUTHOR: M. Montgomery
# DATE:   07.03.2017

import random

RED = '\033[31m'
BLACK = '\033[0m'

SYMBOLS = {
  'SPADES':"\xE2\x99\xA0",
  'CLUBS':"\xE2\x99\xA3",
  'HEARTS':"\xE2\x99\xA5"+BLACK,
  'DIAMONDS':"\xE2\x99\xA6"+BLACK}

class card:
    def __init__(self, suit, val, points=0):
        self.suit = suit        # Hearts, Diamonds, Spades, Clubs
        self.val = val          # e.g. a for ace, 5 for five, 1 for ten
        self.points = points    # point value, e.g. 10 for face cards

        self.name = val[0] + suit[0]
        self.faceup = False
	self.color = RED if self.suit in ['Hearts', 'Diamonds'] else BLACK
        self.colorize = True
        self.useSymbol = True
        self.acesLow = True

    def __repr__(self):
        """ Display -- for facedown cards, otherwise 1-character value & suit letter / symbol. """
        if self.faceup:
            suit = SYMBOLS[self.suit.upper()] if self.useSymbol else self.suit[0]
            return self.color + self.val[0] + suit if self.colorize else\
                   self.val[0] + suit
        else:
            return "--"
                

    def __eq__(self, other):
        return self.name == other.name

    def copy(self):
        """ Return a new card instance equivalent to self. """
        cardCopy = card(self.suit, self.val, self.points)
        cardCopy.faceup = self.faceup 
        cardCopy.colorize = self.colorize 
        cardCopy.useSymbol = self.useSymbol
        cardCopy.acesLow = self.acesLow
        return cardCopy

    def flip(self):
        """ Flip card. """
        self.faceup = False if self.faceup else True

    def flipUp(self):
        """ Make card face up. """
	self.faceup = True

    def flipDown(self):
        """ Make card face down. """
	self.faceup = False


    def isOneLessThan(self, other):
        """ Return true if self has value one less than the other card. """
        order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        if self.acesLow:
            order.insert(0, 'ace')
        else:
            order.append('ace')
        i = order.index(self.val)
        if i < 12 and other.val == order[i+1]:
            return True
        return False

    def isOneMoreThan(self, other):
        """ Return true if self has value one greater than the other card. """
        order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        if self.acesLow:
            order.insert(0, 'ace') 
        else:
            order.append('ace')
        i = order.index(self.val)
        if i > 0 and other.val == order[i-1]:
            return True
        return False

class deck:
    def __init__(self, populate=True):
        self.cards = []

        # make a new deck
	if populate:
            for s in ['Diamonds','Clubs','Hearts','Spades']:
                self.cards.append(card(s, 'ace', 1))       # by default, aces are low
                for v in range(2,11):
                    self.cards.append(card(s, str(v), v))  # suit, value, point value
                for v in ['jack','queen','king']:
                    self.cards.append(card(s, v, 10))
            self.shuffle()
 
        self.colorize = True    # display hearts and diamonds in red
        self.symbol = True      # display suit unicode symbols

    def __repr__(self):
        """ Return list of cards. """
	return str([card.__str__() + ',' for card in self.cards])

    def copy(self):
        """ Return a new deck instance equivalent to self. """
        deckCopy = deck(False)           # don't auto-populate
        deckCopy.repopulate([card for card in self.cards])  # populate with current deck's cards
        deckCopy.colorize = self.colorize
        deckCopy.symbol = self.symbol
        return deckCopy

    def size(self):
        """ Return number of cards in deck. """
        return len(self.cards)

    def empty(self):
        """ Return true if empty. """
        return self.cards == []

    def repopulate(self, cards):
        """ Set deck to new list of cards. """
	self.cards = cards

        # ensure all cards have right color/symbol setting
        if self.colorize:
            self.yesColor()
        if self.symbol:
            self.yesSymbol()

    def shuffle(self):
        """ Shuffle cards into random order.. """
        newDeck = []
        while self.cards != []:
            num = random.randint(0,len(self.cards)-1)
            card = self.cards[num]
            self.cards.pop(num)
            newDeck.append(card)
        self.cards = newDeck

    def deal(self):
        """ Return the topmost card or None if empty. """
	if self.empty():
            return None
        card = self.cards.pop(0)
        return card


    def acesLow(self):
        """ Set aces to low. """
        for card in self.cards:
            if card.val == 'ace':
                card.points = 1
            card.acesLow = True

    def acesHigh(self):
        """ Set aces to high. """
        for card in self.cards:
            if card.val == 'ace':
                card.points = 10
            card.acesLow = False

    def setPoints(self, val, points, suit=""):
        """ Set point value of a card. """
        for card in self.cards:
            if card.val == val:                      # point value of card sometimes changes
                if suit != "" and card.suit == suit: # by suit (e.g. Queen of Spades in Hearts)
                    card.points = points


    def noColor(self):
        """ Turn off displaying hearts and diamonds in red. """
        for card in self.cards:
            card.colorize = False
        self.colorize = False

    def yesColor(self):
        """ Turn on displaying hearts and diamonds in red. """
        for card in self.cards:
            card.colorize = True
        self.colorize = True

    def toggleColor(self):
        """ Toggle displaying hearts and diamonds in red. """
        if self.colorize:
            self.noColor()
        else:
            self.yesColor()


    def noSymbol(self):
        """ Turn off displaying suit unicode symbols. """
        for card in self.cards:
            card.useSymbol = False
        self.symbol = False

    def yesSymbol(self):
        """ Turn on displaying suit unicode symbols. """
        for card in self.cards:
            card.useSymbol = True
        self.symbol = True

    def toggleSymbol(self):
        """ Toggle suit unicode symbol display. """
        if self.symbol:
            self.noSymbol()
        else:
            self.yesSymbol()


class pile(deck):
    """ A stack of cards, with any facedown cards 'beneath' faceup cards. """

    def __init__(self, populate=False, cards=[]):
        
        # make a deck
        deck.__init__(self, populate)
        if cards != []:
            self.cards = cards

        # get index of first facedown card in list
        self.stackIndex = 0
        for i in range(len(self.cards)-1, -1, -1):
            if not self.cards[i].faceup:
                self.stackIndex = i
                break

    def __repr__(self):
        """ Display pile as __ when empty or a list of cards. """
        if self.empty():
            return ['__']
        return [card.__repr__() for card in self.cards]

    def copy(self):
        """ Return a new deck instance equivalent to self. """
        pileCopy = pile(False, [card for card in self.cards]) 
        pileCopy.colorize = self.colorize
        pileCopy.symbol = self.symbol
        return pileCopy

    def add(self, card, visible=False):
        """ Add faceup card to top of stack; 
            slip facedown card in stack as the topmost facedown. """
        if visible:
            card.flipUp()
            self.cards.append(card)           # last card in list is topmost on stack
        else:
            self.cards.insert(self.stackIndex+1, card) # add to top of facedown stack
            self.stackIndex += 1

    def remove(self, index=1):
        """ Remove card at given index. """
        self.cards.pop(-index)         # remove 'top' card by default

    def get(self, index=1):
        """ Return card at given index from top down. """
        if not self.empty():
            return self.cards[-index]  # return 'top' card by default

    def top(self):
        """ Return topmost card. """
        return self.get()

    def numFaceup(self):
        """ Return number of faceup cards. """
        total = 0
        for card in self.cards:
            if card.faceup:
                total += 1
        return total


