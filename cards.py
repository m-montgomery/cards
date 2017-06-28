#!/bin/bash
# TITLE:  cards.py
# AUTHOR: M. Montgomery
# DATE:   06.28.2017

import random

RED = '\033[31m'
BLACK = '\033[0m'

UNICODES = {
  'SPADES':"\xE2\x99\xA0",
  'CLUBS':"\xE2\x99\xA3",
  'HEARTS':RED+"\xE2\x99\xA5"+BLACK,
  'DIAMONDS':RED+"\xE2\x99\xA6"+BLACK}

class card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
        self.name = val[0] + suit[0]
        self.faceup = False
	self.color = RED if self.suit in ['Hearts', 'Diamonds'] else BLACK

    def __repr__(self):
        return self.color + self.val[0] + UNICODES[self.suit.upper()] if self.faceup else "--"

    def flip(self):
        if self.faceup:
            self.faceup = False
        else:
            self.faceup = True

    def flipUp(self):
	self.faceup = True

    def flipDown(self):
	self.faceup = False


class deck:
    def __init__(self, populate=True):
        self.cards = []
	if populate:
            for s in ['Diamonds','Clubs','Hearts','Spades']:
                for v in range(2,11):
                    self.cards.append(card(s, str(v)))
                for v in ['jack','queen','king','ace']:
                    self.cards.append(card(s, v))

    def __repr__(self):
	return str([card.__str__() + ',' for card in self.cards])

    def empty(self):
        return self.cards == []

    def repopulate(self, cards):
	self.cards = cards

    def shuffle(self):
        newDeck = []
        while self.cards != []:
            num = random.randint(0,len(self.cards)-1)
            card = self.cards[num]
            self.cards.pop(num)
            newDeck.append(card)

        self.cards = newDeck

    def deal(self):
	if self.empty():
            return None
        card = self.cards.pop(0)
        return card


class pile(deck):
    def __init__(self, populate=False, cards=[]):
        deck.__init__(self, populate)
        if cards != []:
            self.cards = cards
        self.stackIndex = 0                    # index of first facedown card in list
        for i in range(len(self.cards)-1, -1, -1):
            if not self.cards[i].faceup:
                self.stackIndex = i
                break

    def __repr__(self):
        if self.empty():
            return ['__']
        return [card.__repr__() for card in self.cards]

    def add(self, card, visible=False):
        if visible:
            card.flipUp()
            self.cards.append(card)           # last card in list is topmost on stack
        else:
            self.cards.insert(self.stackIndex+1, card) # add to top of facedown stack
            self.stackIndex += 1

    def remove(self, index=-1):
        self.cards.pop(index)         # remove 'top' card by default

    def get(self, index=-1):
        if not self.empty():
            return self.cards[index]  # return 'top' card by default

    def top(self):
        return self.get()

    def numFaceup(self):
        tot = 0
        for c in self.cards:
            if c.faceup:
                tot += 1
        return tot


