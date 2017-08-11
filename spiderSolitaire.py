# TITLE:  spiderSolitaire.py
# AUTHOR: M. Montgomery
# DATE:   07.12.2017

# USAGE:  python spiderSolitaire.py 

from cards import *


class OrderException(Exception):
    pass

class ColorException(Exception):
    pass

class EmptyException(Exception):
    pass

class spiderDeck(pile):

    def __init__(self, populate=False, suitNum=1):

        pile.__init__(self, False)  # don't auto-populate pile
        if populate:

            suits = ['Clubs','Hearts','Spades','Diamonds']
            suits = suits[:suitNum]

            while len(self.cards) < 104:                       # 2 decks' worth
                for s in suits:
                    self.cards.append(card(s, 'ace', 1))       # by default, aces are low
                    for v in range(2,11):
                        self.cards.append(card(s, str(v), v))  # suit, value, point value
                    for v in ['jack','queen','king']:
                        self.cards.append(card(s, v, 10))
            self.shuffle()
            for c in self.cards:
                c.flipDown()


class spiderSolitaire:
    def __init__(self, suitNum=1):

        self.drawDeck = spiderDeck(True)     # True: want to auto-populate the deck
        self.suitNum = suitNum               # single suit by default
        self.linesWritten = 0

        self.hand = []
        for _ in range(10):                  # 10 piles in spider solitaire
            self.hand.append(pile())         # (numbering 1 - 10 for simplicity)

	# deal cards into 10 piles
        for i in range(4):
            for _ in range(5):
                self.hand[i].add(self.drawDeck.deal())   # add 5 facedown
        for i in range(4, 10):
            for _ in range(4):
                self.hand[i].add(self.drawDeck.deal())   # add 4 facedown
        for i in range(10):
            self.hand[i].add(self.drawDeck.deal(), True)   # add 1 faceup
        

    def __repr__(self):
        text = ''

        # display pile numbers
        for i in range(10):
	    text += str(i) + '. '
        text += "Deck"
        drawsLeft = self.drawDeck.size() // 10
	
	# display hand
	piles = []
	for i in range(10):
            piles.append(self.hand[i].__repr__())
        last = max([len(pile) for pile in piles])
        for i in range(last):
            text += '\n'
            for pile in piles:
                if i < len(pile):
                    text += pile[i] + ' '
                else:
                    text += '   '
            if i < drawsLeft:       # display deals left
                text += '  --'
        text += "\n"

        self.linesWritten = len(text.split('\n'))
        return text
  
 
    def error(self, msg):
        """ Display error message, increment lines written. """
        self.linesWritten += 2
        print("Error: " + msg)
        t = raw_input("Hit enter to continue: ")


    def copy(self):
        """ Return a new spiderSolitaire game copy of self. """
        gameCopy = spiderSolitaire(self.suitNum)

        gameCopy.drawDeck = self.drawDeck.copy()

        for i in range(10):
            gameCopy.hand[i] = self.hand[i].copy()

        gameCopy.linesWritten = self.linesWritten

        return gameCopy


    def clear(self):
        """ Clear terminal screen. """
        print("\033[1;0H")
        for _ in range(self.linesWritten):
            print("                                                                      ")
        print("\033[1;0H")


    def play(self):
        """ Main execution loop for gameplay. """

        # get user choice
	choice = ""
	while choice != "e":
            
            # display game
            self.clear()
 	    print(self)
	    print("Enter... \n- d to deal \n- # of pile to move from \n- c to auto-complete \n- o for options \n- e to exit \n")
            choice = raw_input("Choice: ")
            self.linesWritten += 8 

            # call appropriate method
	    if choice == "d":               # deal from deck
                self.deal()
	    elif choice == "e":             # quit game
		continue 
            elif choice == "c":             # try to auto-complete
                if self.autocomplete():
                    choice = "e"
            elif choice == "o":             # display options
                self.options()
            else:                           # move card(s)
                try:
	            fromPile = int(choice)
		    self.move(fromPile)
	        except ValueError:
                    self.error("From pile # must be between 1 and 10.")
                    continue

                # check for win
	        choice = self.checkWin()
            
            # remove any complete King-Ace piles
            self.checkPileDone()
	    
    def checkPileDone(self):
        """ Check for completed piles. """

        order = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        for i in range(10):
            pile = self.hand[i]
            if pile.numFaceup() < 13:
                continue

            complete = True
            cards = []
            for i in range(1, pile.numFaceup() + 1):
                cards.append(pile.get(i))
           
            suit = cards[0].suit
            for j in range(len(cards)):
                if cards[j].val != order[j]:
                    complete = False
                elif cards[j].suit != suit:
                    complete = False

            if complete:
                for _ in range(13):
                    pile.remove()
                pile.top().flipUp()


    def checkWin(self):
        """ Check for completed game. """
        return False

        self.clear()
        print("\nYOU WON!!")
        print(self)
        print('')
        return "e"       # for exit


    def autocomplete(self):
        """ Attempt to auto-complete the game. """
        if not (self.drawDeck.empty()): 
            print("There are still cards in the draw deck. Cannot auto-complete.")
            return False

        gameCopy = self.copy()
        stuck = False
        while not stuck:
            stuck = True            # assume no cards were moved
            # try to move top card from each pile to suit pile
            for pile in gameCopy.hand:
                try:
                    result = gameCopy.moveTo(pile) 
                except:         # don't report exceptions
                    continue
                
                stuck = False   # successfully moved a card

            if gameCopy.checkWin() == "e":
                return True 

        print("Unable to auto-complete. Keep trying!")
        return False


    def moveTo(self, FROM, TO, numCards): 
        """ Attempt to move card(s) to another pile. """

        if FROM.empty():
            return False

        # make copies to edit
        toCopy = TO.copy()
        fromCopy = FROM.copy()

        # try to move each card, test for errors
        if not TO.empty():
            for i in range(numCards, 0, -1):
                card = fromCopy.get(i)
                # must move onto card 1 greater than self
                if not card.isOneLessThan(toCopy.top()):
                    raise OrderException
                # must move onto card of same color
                elif not self.colorMatch(card, toCopy.top()):
                    raise ColorException
            
                toCopy.add(card, True)
                fromCopy.remove(i)

        # no errors, go ahead and move for real
        for i in range(numCards, 0, -1):
            TO.add(FROM.get(i), True)
            FROM.remove(i)

        return True
    

    def deal(self):
        """ Deal cards from the draw deck. """

        for i in range(10):
            if not self.drawDeck.empty():
                c = self.drawDeck.top()
                self.drawDeck.remove()
                self.hand[i].add(c, True)


    def move(self, fromPile):
	# get TO pile
	toPile = raw_input("To pile #: ")
	try:
	    toPile = int(toPile)
	except ValueError:
	    toPile = None
        self.linesWritten += 1

	# make sure FROM and TO piles are valid
	if fromPile not in range(10):
	    self.error("Can only move cards from piles 1 - 10.")
	    return	
	if toPile not in range(10):
	    self.error("Can only move cards to piles 1 - 10.")
	    return
	if fromPile == toPile:
	    self.error("From and to piles must be different.")
	    return

	# get FROM and TO pile instances
	FROM = self.hand[fromPile] 
	TO = self.hand[toPile]

	# get number of cards to move
	numCards = raw_input("Number of cards: ")
	try:
	    numCards = int(numCards)
	except ValueError:
	    numCards = FROM.numFaceup()   # assume move all faceup cards
	print("")
        self.linesWritten += 2
	
	# make sure number of cards is valid
	if numCards > FROM.numFaceup():
	    self.error("There aren't " + str(numCards) + " faceup cards on that pile.")
	    return

        # moving cards need to be consecutive & color-alternating
	for i in range(1, numCards):
            if not self.colorMatch(FROM.get(i), FROM.get(i+1)):
                self.error("Cards do not have correct colors.")
                return
            if not FROM.get(i).isOneLessThan(FROM.get(i+1)):
                self.error("Cards are not properly consecutive.")
		return
        
        # try to move the cards
        try:
            result = self.moveTo(FROM, TO, numCards) 
        except OrderException:
            self.error("Cards are not properly consecutive.")
            return
        except ColorException:
            self.error("Cards do not have correct colors.")
            return
        print("")
        self.linesWritten += 1
 
	# flip over a card if applicable
	if not FROM.empty():
	    FROM.top().flipUp()


    def colorMatch(self, a, b):
	""" Make sure colors match. """

        # must be same color
	if (a.suit in ['Spades', 'Clubs'] and b.suit in ['Diamonds', 'Hearts']) or\
	(a.suit in ['Diamonds', 'Hearts'] and b.suit in ['Spades', 'Clubs']):
            return False

        return True


    def options(self):
        print("Game options: enter...")
        print("- c to toggle colored-text display")
        print("- s to toggle suit symbol display")
        choice = raw_input("Choice: ")
        # toggle color display
        if choice == "c":
            for deck in self.hand:
                deck.toggleColor()
            for deck in [self.dPile, self.hPile, self.cPile, self.sPile]:
                deck.toggleColor()
            self.drawDeck.toggleColor()
        # toggle symbol display
        elif choice == "s":
            for deck in self.hand:
                deck.toggleSymbol()
            for deck in [self.dPile, self.hPile, self.cPile, self.sPile]:
                deck.toggleSymbol()
            self.drawDeck.toggleSymbol()
        # toggle draw style
        print("")
        self.linesWritten += 6


def main():
    game = spiderSolitaire()
    game.play()

main()

