# TITLE:  solitaire.py
# AUTHOR: M. Montgomery
# DATE:   07.03.2017

# USAGE:  python solitaire.py 

from cards import *

class manager:
    def __init__(self):
        self.drawDeck = pile(True)      # True: want to auto-populate the deck
        self.drawDeck.shuffle()
	self.discardDeck = []
	self.drawnCard = None
        self.drawStyle = 1              # default is 1-card draw

	# make 4 empty suit piles
        self.dPile = pile()
        self.hPile = pile()
        self.sPile = pile()
        self.cPile = pile()
        self.hand = []
        for _ in range(7):
            self.hand.append(pile())

	# deal cards into 7 piles
        for i in range(7):
            self.hand[i].add(self.drawDeck.deal(), True)
            for j in range(i+1,7):
                self.hand[j].add(self.drawDeck.deal())

    def __repr__(self):
        text = ''

	# display suit piles (assumes color & symbol display)
        text += RED + SYMBOLS['HEARTS'] + BLACK + ' '
        text += SYMBOLS['SPADES'] + ' '
        text += RED + SYMBOLS['DIAMONDS'] + BLACK + ' '
        text += SYMBOLS['CLUBS'] + ' '
	
        text += ' '*6 + '0.\n'
        for p in [self.hPile, self.sPile, self.dPile, self.cPile]:
	    if p.empty():
		text += '__ '       
     	    else:
		text += p.top().__repr__() + ' '

	# display draw pile 
 	if self.drawnCard != None:
            text += '   ' + self.drawnCard.__repr__() + ' '
	else:
            text += ' '*6
        if self.drawDeck.empty():
	    text += '__\n\n'
	else:
    	    text += '??\n\n'

        for i in range(1,8):
	    text += str(i) + '. ' 
	
	# display hand
	piles = []
	for p in self.hand:
            piles.append(p.__repr__())
        last = max([len(pile) for pile in piles])
        for i in range(last):
            text += '\n'
            for pile in piles:
                if i < len(pile):
                    text += pile[i] + ' '
                else:
                    text += '   '

        return text


    def play(self):
        """ Main execution loop for gameplay. """

        # get user choice
	choice = ""
	while choice != "e":
	    print(self)
	    print("Enter... \n- d to draw \n- # of pile to move from \n- c to auto-complete \n- o for options \n- e to exit \n")
            choice = raw_input("Choice: ")

            # call appropriate method
	    if choice == "d":        # draw from deck
                self.draw()
	    elif choice == "e":      # quit game
		continue 
            elif choice == "c":      # try to auto-complete
                self.autocomplete()
            elif choice == "o":      # display options
                self.options()
            else:                    # move card(s)
	        try:
	            fromPile = int(choice)
		    self.move(fromPile)
	        except ValueError:
	            print("From pile # must be between 0 and 8.")
	            continue

                # check for win
	        if self.win():
		    print("\nYOU WON!!")
		    print(self)
		    choice = "e"
	    

    def win(self):
        """ Check for completed game. """
        for p in [self.dPile, self.hPile, self.sPile, self.cPile]:
	    if len(p.cards) != 13:       # assumes all errors were caught previously
		return False
	return True

    def autocomplete(self):
        """ Attempt to auto-complete the game. """
        if not self.drawDeck.empty():
            print("There are still cards in the draw deck. Cannot auto-complete.")
            return
        
    def toggleDraw(self):
        """ Toggle draw style between 1- and 3-card draw. """
        self.drawStyle = 3 if self.drawStyle == 1 else 1


    def draw(self):
        """ Draw a card from the draw deck. """
	# repopulate the draw deck
	if self.drawDeck.empty():
            if self.discardDeck != []:
                self.drawDeck.repopulate(self.discardDeck)
                self.discardDeck = []
            else:
                print("There are no more cards in the draw pile.")
		return

	# move old card
        old = self.drawnCard
	if old != None:
      	    old.flipDown()
	    self.drawDeck.remove()
	    self.discardDeck.insert(0, old)

        # draw 1 card
        if self.drawStyle == 1:
            self.drawnCard = self.drawDeck.top()
        # draw 3 cards
        else:
            # move first 2 cards to discard
            if self.drawDeck.size() >= 3:
               for _ in range(2):
                   c = self.drawDeck.top()
                   self.drawDeck.remove()
                   self.discardDeck.insert(0, c)
               self.drawnCard = self.drawDeck.top()

            # move discard back to draw deck, take 3rd card
            elif self.drawDeck.size() + self.discardDeck.size() >= 3:
                if self.drawDeck.size() == 2:
                    for _ in range(2):
                        c = self.drawDeck.top()
                        self.drawDeck.remove()
                        self.discardDeck.insert(0, c)
                    self.drawDeck.repopulate(self.discardDeck)
                    self.discardDeck = []
                    self.drawnCard = self.drawDeck.top()
                else:
                    c = self.drawDeck.top()
                    self.drawDeck.remove()
                    self.discardDeck.insert(0, c)
                    self.drawDeck.repopulate(self.discardDeck)
                    self.discardDeck = []

                    c = self.drawDeck.top()
                    self.drawDeck.remove()
                    self.discardDeck.insert(0, c)
                    self.drawnCard = self.drawDeck.top()

            # display only card
            else:
                for _ in range(self.drawDeck.size()):
                    c = self.drawDeck.top()
                    self.drawDeck.remove()
                    self.discardDeck.insert(0, c)
                    self.drawDeck.repopulate(self.discardDeck)
                    self.discardDeck = []
                    self.drawnCard = self.drawDeck.top()

	if self.drawnCard is not None:
	    self.drawnCard.flipUp()       # new card face up


    def move(self, fromPile):
	# get TO pile
	toPile = raw_input("To pile #: ")
	try:
	    toPile = int(toPile)
	except ValueError:
	    toPile = toPile.upper()

	# make sure FROM and TO piles are valid
	if fromPile not in range(8):
	    print("Can only move cards from piles 0 - 7.")
	    return	
	if toPile not in range(1,8) and toPile not in ['H', 'C', 'D', 'S']:
	    print("Can only move cards to piles 1 - 7 and piles H, C, D, and S.")
	    return
	if fromPile == toPile:
	    print("From and to piles must be different.")
	    return

	# get FROM and TO pile instances
	FROM = self.hand[fromPile-1] if fromPile in range(1,8) else self.drawDeck
	if toPile in range(1,8):
	    TO = self.hand[toPile-1]
	else:
	    pileOps = {'H': self.hPile, 'C': self.cPile, 'D': self.dPile, 'S': self.sPile}
	    TO = pileOps[toPile]

	# get number of cards to move
	numCards = raw_input("Number of cards: ")
	try:
	    numCards = int(numCards)
	except ValueError:
	    numCards = FROM.numFaceup()   # assume move all faceup cards
	print('')
	
	# make sure number of cards is valid
	if numCards > FROM.numFaceup():
	    print("There aren't " + str(numCards) + " faceup cards on that pile.")
	    return
	elif toPile not in range(1,8) and numCards > 1:
	    print("Can only move one card at a time to a suit pile.")
	    return

	# if to pile is an empty pile, top from card must be king or ace, depending
	topFromCard = FROM.get(-numCards)
	if TO.empty() and toPile in range(1,8) and topFromCard.val != 'king':
	    print("Can only move kings to empty spaces.")
	    return
	elif TO.empty() and toPile not in range(1,8) and topFromCard.val != 'ace':
	    print("Can only move aces to empty suit piles.")
	    print("You tried to move: " + str(topFromCard))
	    return

	# moving cards need to be consecutive & color-alternating
	for i in range(-1, -numCards, -1):
	    if not self.colorMatch(FROM.get(i), FROM.get(i-1)):
	        print(str(FROM.get(i)) + " must be a different color than " +\
	              str(FROM.get(i-1)))
	        return
            if not FROM.get(i).isOneLessThan(FROM.get(i-1)):

		print("Cards aren't consecutive; " + str(FROM.get(i)) +\
		      " is not one less than " + str(FROM.get(i-1)))
		return

	# to and from need to be consecutive & correct colors
	if not TO.empty():
	    toCard = TO.top()
	    if not self.colorMatch(topFromCard, toCard, toPile):
	        print(str(topFromCard) + " must be a different color than " + str(toCard))
	        return	
	    
	    # moving to suit pile; to pile card must be smaller
	    if toPile not in range(1,8):
                if not topFromCard.isOneMoreThan(toCard):
	       	    print("Cards aren't consecutive; " + str(topFromCard) +\
                          " is not one more than " + str(toCard))
	    	    return
	    # moving to hand pile; to pile card must be higher
	    else:
                if not topFromCard.isOneLessThan(toCard):
		    print("Cards aren't consecutive; " + str(topFromCard) +\
                          " is not one less than " + str(toCard))
		    return

	# move the card!
	toMove = []
	for _ in range(numCards):
	    toMove.insert(0, FROM.top())  # flip order; make sure moving top card first
	    FROM.remove()
	for c in toMove:
	    TO.add(c, True)
	   
	# flip over a card if applicable
	if fromPile != 0 and not FROM.empty():
	    FROM.top().flipUp()

	# handle draw deck
	if fromPile == 0 and self.discardDeck != []:
	    lastCard = self.discardDeck[0]         # bring back last drawn card
	    self.drawDeck.add(lastCard, True)
	    self.discardDeck.pop(0)
	    self.drawnCard = lastCard
	elif fromPile == 0 and not FROM.empty():
	    FROM.top().flipUp()
	    self.drawnCard = FROM.top()
	elif fromPile == 0:
	    self.drawnCard = None


    def colorMatch(self, a, b, toPile=1):
	# moving to hand pile; must be alternating color
	if toPile in range(1,8):
	    if a.suit in ['Spades', 'Clubs']:
	        return b.suit in ['Diamonds', 'Hearts']
	    return b.suit in ['Spades', 'Clubs']
	# moving to suit pile; must be same color
	else:
	    if a.suit in ['Spades', 'Clubs']:
	        return b.suit in ['Spades', 'Clubs']
	    return b.suit in ['Diamonds', 'Hearts']


    def options(self):
        print("Game options: enter...")
        print("- c to toggle colored-text display")
        print("- s to toggle suit symbol display")
        print("- d to toggle draw style (1 or 3 cards)")
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
        elif choice == "d":
            self.toggleDraw()
        print('')


def main():
    soli = manager()
    soli.play()

main()

