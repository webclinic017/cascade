#this program creates a sudoku board as an array and performs a wave function collapse to generate random numbers

from pprint import pprint
from datetime import date
from datetime import timedelta
from dotenv import load_dotenv
import random
import os
import alpaca_trade_api as alpaca_api
import pandas as pd
import inspect

#an organized class for stocks/crypto trading
class Trader:
	#initialization of the trader class
	def __init__(self):
		#load the environment variables from the .env file
		load_dotenv()

		#set up the alpaca REST client
		self.alpaca, self.alpaca_paper = self.setupAlpaca()

		#select a random stock from the s&p 500
		stocks = self.snp500()
		randomindex = random.randint(0, len(stocks)-1)
		currentstock = stocks[randomindex]

		print(currentstock)
		print(self.getStockBar(currentstock).close)

	#a function that sets up the alpaca REST client
	def setupAlpaca(self):
		#get information to use the alpaca api using the os module
		api_secret = os.environ["API_SECRET"]
		api_key = os.environ["API_KEY"]
		base_url = os.environ["BASE_URL"]
		paper_url = os.environ["PAPER_URL"]

		#initialize the REST client for the alpaca api
		alpaca = alpaca_api.REST(api_key, api_secret, base_url)

		#initialize the paper trading REST client
		alpaca_paper = alpaca_api.REST(api_key, api_secret, paper_url)

		return alpaca, alpaca_paper

	#returns a list of the stocks on the S&P 500 in random order
	def snp500(self):
		#get a list of the stocks on the current S&P 500 from wikipedia
		table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

		#get the raw values of the stock symbols from the wikipedia data
		df = table[0]
		symbols = df.loc[:,"Symbol"].values

		#shuffle the values of the stock to make random selections
		random.shuffle(symbols)

		return symbols

	#gets the latest bar of a stock based on the symbol
	def getStockBar(self, symbol):
		stockprice = self.alpaca.get_latest_bar(symbol)

		return stockprice

	#places an order for a stock
	def buyStock(self, symbol, money):
		#check to see if this stock is fractionable
		fractionable = self.alpaca.get_asset(symbol)
		fractionable = fractionable.fractionable

		#place an order or return False depending on if the stock is fractional
		if (fractionable):
			#place an order for fractional shares
			return self.alpaca.submit_order(
				symbol=symbol,
				notional=money,
				side="buy",
				type="market",
				time_in_force="day"
			)
		else:
			#the stock is not fractionable so it cannot be bought
			return False

	#returns a list of the crypto available on alpaca in random order
	def cryptoCoins(self):
		#array of the accepted coin symbols on alpaca
		coins = [
			"AAVEUSD",
			"ALGOUSD",
			"AVAXUSD",
			"BATUSD",
			"BTCUSD",
			"BCHUSD",
			"LINKUSD",
			"DAIUSD",
			"DOGEUSD",
			"ETHUSD",
			"GRTUSD",
			"LTCUSD",
			"MKRUSD",
			"MATICUSD",
			"NEARUSD",
			"PAXGUSD",
			"SHIBUSD",
			"SOLUSD",
			"SUSHIUSD",
			"USDTUSD",
			"TRXUSD",
			"UNIUSD",
			"WBTCUSD",
			"YFIUSD"
		]

		#shuffle the coin values for random selections
		random.shuffle(coins)

		return coins

	#gets the latest bar of a cryptocurrency based on the symbol and exchange (default exchange is FTX)
	def getCryptoBar(self, symbol, exchange="FTXU"):
		#select the latest crypto bar from specified exchange, the exchanges can be coinbase (CBSE), FTX (FTXU), or ErisX (ERSX)
		cryptoprice = self.alpaca.get_latest_crypto_bar(symbol, exchange)

		return cryptoprice


#an organized class for the cascade algorithm
class Cascade:
	#initialization of the cascade
	def __init__(self):
		self.board = self.createBoard()

	#creates a blank sudoku board with all cells in a superposition
	def createBoard(self):
		mainarray = []

		for x in range(9):
			temparray = []
			for y in range(9):
				temparray.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
			mainarray.append(temparray)

		return mainarray

	#prints all of the values in the sudoku board
	def boardValues(self):
		valuesarr = []

		for x in range(9):
			for y in range(9):
				for num in self.board[x][y]:
					valuesarr.append(num)

		return valuesarr

	#randomly collapses a cell on the board to a single state
	def randomCollapse(self, subgrid=random.randint(0, 8), cell=random.randint(0, 8)):
		#get the values for the subgrid, cell, and state of the cell
		randomsubgrid = subgrid
		randomcell = cell

		#set values for the cell with a single state
		self.subgrid = randomsubgrid
		self.cell = randomcell

		#check the solved subgrid, row, and column values to collapse the possibilities of the current cell
		solvedarray = self.subgridValues() + self.rowValues() + self.columnValues()

		#check the solved cells surrounding this cell to remove impossible states
		for i in solvedarray:
			if (i in self.board[randomsubgrid][randomcell] and len(self.board[randomsubgrid][randomcell]) > 1):
				self.board[randomsubgrid][randomcell].remove(i)

		#randomly select a state for this cell to collapse to
		randomindex = random.randint(0, len(self.board[randomsubgrid][randomcell])-1)
		randomstate = self.board[randomsubgrid][randomcell][randomindex]
		self.board[randomsubgrid][randomcell] = [randomstate]
		self.state = randomstate

		#collapse the subgrid, row, and column associated with this cell
		self.collapseSubgrid()
		self.collapseRow()
		self.collapseColumn()

		#get the value of the cell with the least entropy
		subgrid, cell, solved = self.entropyCollapse()

		#check to see if the board is solved as the exit condition for this function
		if (not solved):
			#randomly collapse the cell with the least entropy
			self.randomCollapse(subgrid, cell)

		return self.board

	#collapses the cell with the least entropy on the board
	def entropyCollapse(self):
		'''
		set a starting length of possibilities and a cell on the board to compare to when
		finding the lowest entropy cell. also set a count variable to count the amount of
		solved cells there are on the board. if the solved cell count is 81, then the
		board is solved
		'''
		length = 9
		subgrid = 0
		cell = 0
		count = 0

		#find a cell with the shortest length of possibilities (least entropy)
		for x in range(9):
			for y in range(9):
				cellentropy = len(self.board[x][y])

				if (cellentropy < length and cellentropy > 1):
					subgrid = x
					cell = y
					length = cellentropy
				elif (cellentropy == 1):
					count += 1

		#check to see if the board is solved or not
		if (count == 81):
			return subgrid, cell, True
		else:
			return subgrid, cell, False

	#a function to return the values of numbers in a subgrid
	def subgridValues(self):
		valuesarr = []

		for i in range(9):
			if (len(self.board[self.subgrid][i]) == 1):
				valuesarr.append(self.board[self.subgrid][i][0])

		return valuesarr

	#collapses the subgrid of a board based on the state of a single cell
	def collapseSubgrid(self):
		for i in range(9):
			if (i != self.cell and self.state in self.board[self.subgrid][i] and len(self.board[self.subgrid][i]) > 1):
				self.board[self.subgrid][i].remove(self.state)


	#a function to get the correct range of indexes based on a subgrid or cell number (works only for rows and subgrids, not columns)
	def getrowrange(self, number):
		if (number in range(0, 3)):
			rowrange = range(0, 3)
		elif (number in range(3, 6)):
			rowrange = range(3, 6)
		elif (number in range(6, 9)):
			rowrange = range(6, 9)

		return rowrange

	#a function to return the values of numbers in a row
	def rowValues(self):
		subgridrange = self.getrowrange(self.subgrid)
		cellrange = self.getrowrange(self.cell)

		valuesarr = []

		for s in subgridrange:
			for c in cellrange:
				if (len(self.board[s][c]) == 1):
					valuesarr.append(self.board[s][c][0])

		return valuesarr

	#a function to collapse the possibilities of a row in the board
	def collapseRow(self):
		#get the correct ranges for the subgrid and cell indexes to collapse the possibilities of
		subgridrange = self.getrowrange(self.subgrid)
		cellrange = self.getrowrange(self.cell)

		#collapse the possibilities of cells in the same row as the initial collapsed cell
		for s in subgridrange:
			for c in cellrange:
				if (self.state in self.board[s][c] and len(self.board[s][c]) > 1):
					self.board[s][c].remove(self.state)

	#a function to get the correct index numbers based on a subgrid or cell number (works only for columns, not rows or subgrids)
	def getcolumnrange(self, number):
		if (number in [0, 3, 6]):
			columnrange = [0, 3, 6]
		elif (number in [1, 4, 7]):
			columnrange = [1, 4, 7]
		elif (number in [2, 5, 8]):
			columnrange = [2, 5, 8]

		return columnrange

	#a function to return the values of numbers in a column
	def columnValues(self):
		subgridcolumn = self.getcolumnrange(self.subgrid)
		cellcolumn = self.getcolumnrange(self.cell)

		valuesarr = []

		for s in subgridcolumn:
			for c in cellcolumn:
				if (len(self.board[s][c]) == 1):
					valuesarr.append(self.board[s][c][0])

		return valuesarr

	#a function to collapse the possibilities of a column in the board
	def collapseColumn(self):
		#get the correct ranges for the subgrid and cell indexes to collapse the possibilities of
		subgridcolumn = self.getcolumnrange(self.subgrid)
		cellcolumn = self.getcolumnrange(self.cell)

		#collapse the possibilities of cells in the same column as the initial collapsed cell
		for s in subgridcolumn:
			for c in cellcolumn:
				if (self.state in self.board[s][c] and len(self.board[s][c]) > 1):
					self.board[s][c].remove(self.state)

trader = Trader()

#make a cascade instance and generate a random board
cascade = Cascade()
solvedboard = cascade.randomCollapse()
boardvalues = cascade.boardValues()

print("****The Solved Sudoku Board***")
pprint(solvedboard)
print("")

print("****The Sudoku Board Values****")
print(boardvalues)
