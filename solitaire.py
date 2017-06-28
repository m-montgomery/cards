# TITLE:  solitaire.py
# AUTHOR: M. Montgomery
# DATE:   06.28.2017

# USAGE:  python solitaire.py 

from cards import *
VALUES = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

RED='\033[0;31m'
NC='\033[0m'
# ex: echo -e "Print ${RED}this${NC} in red."


class manager:
    def __init__(self):
        self.drawDeck = pile(True)      # want to populate the deck
        self.drawDeck.shuffle()
	self.discardDeck = []
	self.drawnCard = None

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

	# display suit piles
	for suit in ['HEARTS', 'SPADES', 'DIAMONDS', 'CLUBS']:
	    text += UNICODES[suit] + '  '
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
	choice = ""
	while choice != "e":
	    print(self)
	    print('')
            choice = raw_input("Enter d to draw, pile # to move from, or e to exit: ")
	    if choice == "d":
                self.draw()
	    elif choice == "e":
		continue
            else:
	        try:
	            fromPile = int(choice)
		    self.move(fromPile)
	        except ValueError:
	            print("From pile # must be between 0 and 8.")
	            continue
	    if self.win():
		print("\nYOU WON!!")
		print(self)
		choice = "e"
	    

    def win(self):
        for p in [self.dPile, self.hPile, self.sPile, self.cPile]:
	    if len(p.cards) != 13:       # assumes all errors were caught previously
		return False
	return True


    def draw(self):
	# repopulate the draw deck
	if self.drawDeck.empty():
            if self.discardDeck != []:
                self.drawDeck.repopulate(self.discardDeck)
                self.discardDeck = []
            else:
                print("There are no more cards in the draw pile.")
		return

	# move old card; flip new card
        old = self.drawnCard
	if old != None:
      	    old.flipDown()
	    self.drawDeck.remove()
	    self.discardDeck.insert(0,old)
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
	    index = VALUES.index(FROM.get(i).val) + 1
	    if index < 13 and VALUES[index] != FROM.get(i-1).val:
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
	        index = VALUES.index(topFromCard.val) - 1
	        if VALUES[index] != toCard.val:
	       	    print("Cards aren't consecutive; " + str(topFromCard) +\
                          " is not one more than " + str(toCard))
	    	    return
	    # moving to hand pile; to pile card must be higher
	    else:
	        index = VALUES.index(topFromCard.val) + 1
	        if VALUES[index] != toCard.val:
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
	    self.drawnCard = FROM.top()   # ?
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


def main():
    soli = manager()
    soli.play()

main()

