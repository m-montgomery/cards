# TITLE:  solitaire.py
# AUTHOR: M. Montgomery
# DATE:   07.10.2017

# USAGE:  python solitaire.py 

from cards import *


class OrderException(Exception):
    pass

class ColorException(Exception):
    pass

class EmptyException(Exception):
    pass

class NotEmptyException(Exception):
    pass

class AcesStartException(Exception):
    pass


class solitaire:
    def __init__(self):

        self.drawDeck = pile(True)      # True: want to auto-populate the deck
        self.drawDeck.shuffle()
	self.discardDeck = []
	self.drawnCard = None
        self.drawStyle = 1              # default is 1-card draw
        self.linesWritten = 0

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
        text += RED + SYMBOLS['HEARTS'] + BLACK + '  '
        text += SYMBOLS['SPADES'] + '  '
        text += RED + SYMBOLS['DIAMONDS'] + BLACK + '  '
        text += SYMBOLS['CLUBS'] + '  '
	
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

        self.linesWritten = len(text.split('\n'))
        return text
  
 
    def error(self, msg):
        """ Display error message, increment lines written. """
        self.linesWritten += 2
        print("Error: " + msg)
        t = raw_input("Hit enter to continue: ")


    def copy(self):
        """ Return a new solitaire game copy of self. """
        gameCopy = solitaire()

        gameCopy.drawDeck = self.drawDeck.copy()
        gameCopy.discardDeck = [card for card in self.discardDeck]

        gameCopy.hPile = self.hPile.copy()
        gameCopy.dPile = self.dPile.copy()
        gameCopy.sPile = self.sPile.copy()
        gameCopy.cPile = self.cPile.copy()

        for i in range(7):
            gameCopy.hand[i] = self.hand[i].copy()

        gameCopy.drawnCard = self.drawnCard
        gameCopy.drawStyle = self.drawStyle
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
	    print("Enter... \n- d to draw \n- # of pile to move from \n- c to auto-complete \n- o for options \n- e to exit \n")
            choice = raw_input("Choice: ")
            self.linesWritten += 8 

            # call appropriate method
	    if choice == "d":               # draw from deck
                self.draw()
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
                    self.error("From pile # must be between 0 and 8.")
                    continue

                # check for win
	        choice = self.checkWin()
	    

    def checkWin(self):
        """ Check for completed game. """
        for p in [self.dPile, self.hPile, self.sPile, self.cPile]:
	    if len(p.cards) != 13:       # assumes all errors were caught previously
		return

        self.clear()
        print("\nYOU WON!!")
        print(self)
        print('')
        return "e"       # for exit


    def autocomplete(self):
        """ Attempt to auto-complete the game. """
        if not (self.drawDeck.empty() and self.discardDeck == []):
            print("There are still cards in the draw deck. Cannot auto-complete.")
            return False

        gameCopy = self.copy()
        stuck = False
        while not stuck:
            stuck = True            # assume no cards were moved
            # try to move top card from each pile to suit pile
            for pile in gameCopy.hand:
                try:
                    result = gameCopy.moveToSuit(pile) 
                except:         # don't report exceptions
                    continue
                
                stuck = False   # successfully moved a card

            if gameCopy.checkWin() == "e":
                return True 

        print("Unable to auto-complete. Keep trying!")
        return False


    def moveToHand(self, FROM, TO, numCards): 
        """ Attempt to move card(s) to another pile. """

        if FROM.empty():
            return False

        # make copies to edit
        toCopy = TO.copy()
        fromCopy = FROM.copy()

        # try to move each card, test for errors
        for i in range(numCards, 0, -1):
            card = fromCopy.get(i)
            if card.val != "king":
                # can only move kings to empty
                if toCopy.empty():
                    raise EmptyException
                # must move onto card 1 greater than self
                elif not card.isOneLessThan(toCopy.top()):
                    raise OrderException
                # must move onto card of opposite color
                elif not self.colorMatch(card, toCopy.top()):
                    raise ColorException
            else:
                # can only move kings to empty
                if not toCopy.empty():
                    raise NotEmptyException
            
            toCopy.add(card, True)
            fromCopy.remove(i)

        # no errors, go ahead and move for real
        for i in range(numCards, 0, -1):
            TO.add(FROM.get(i), True)
            FROM.remove(i)

        return True


    def moveToSuit(self, FROM):
        """ Attempt to move a card to its suit pile. """
        
        card = FROM.top()
	if card is None:  # empty piles return None from top()
            return False

        # get suit pile instance
        pileOps = {'H': self.hPile, 'C': self.cPile, 'D': self.dPile, 'S': self.sPile}
        TO = pileOps[card.suit[0].upper()]
        
        # make sure consecutive
        if TO.empty():
            if card.val != "ace":
                raise AcesStartException
                return False
        else:
            if card.val == "ace":
                raise AcesStartException
                return False
            if not card.isOneMoreThan(TO.top()):
                raise OrderException
                return False

        TO.add(card, True)
        FROM.remove()
        return True

        
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
                self.error("There are no more cards in the draw pile.")
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
            elif self.drawDeck.size() + self.discardDeck.size() >= 3:   # improve this section
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
	    toPile = None
        self.linesWritten += 1

	# make sure FROM and TO piles are valid
	if fromPile not in range(8):
	    self.error("Can only move cards from piles 0 - 7.")
	    return	
	if toPile not in range(1,8) and toPile is not None:
	    self.error("Can only move cards to piles 1 - 7 or the suit piles.")
	    return
	if fromPile == toPile:
	    self.error("From and to piles must be different.")
	    return

	# get FROM and TO pile instances
	FROM = self.hand[fromPile-1] if fromPile in range(1,8) else self.drawDeck
	if toPile in range(1,8):
	    TO = self.hand[toPile-1]
	else:
	    pileOps = {'H': self.hPile, 'C': self.cPile, 'D': self.dPile, 'S': self.sPile}
	    try:
                TO = pileOps[FROM.top().suit[0].upper()]
            except:
                return    # probably entered invalid FROM pile #

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
            result = self.moveToHand(FROM, TO, numCards) if toPile in range(1, 8) else self.moveToSuit(FROM)
        except OrderException:
            self.error("Cards are not properly consecutive.")
            return
        except ColorException:
            self.error("Cards do not have correct colors.")
            return
        except NotEmptyException:
            self.error("Kings can only be moved to empty spaces.")  
            return
        except EmptyException:
            self.error("Only kings can be moved to empty spaces.")  
            return
        except AcesStartException:
            self.error("Only aces can start suit piles.")
            return
        print("")
        self.linesWritten += 1
 
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
	""" Make sure colors match. By default assumes color must alternate. """

        # moving to hand pile; must be alternating color
	if toPile in range(1,8):
	    if (a.suit in ['Spades', 'Clubs'] and b.suit in ['Spades', 'Clubs']) or\
	    (a.suit in ['Diamonds', 'Hearts'] and b.suit in ['Diamonds', 'Hearts']):
	        return False
        # moving to suit pile; must be same color
	else:
	    if (a.suit in ['Spades', 'Clubs'] and b.suit in ['Diamonds', 'Hearts']) or\
	    (a.suit in ['Diamonds', 'Hearts'] and b.suit in ['Spades', 'Clubs']):
                return False

        return True


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
        print("")
        self.linesWritten += 6


def main():
    game = solitaire()
    game.play()

main()

