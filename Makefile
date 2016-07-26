CC=g++
CFLAGS=-g -c -Wall -std=gnu++11
LDFLAGS=-g -Wall -std=gnu++11

SOURCES=smashbot.cpp
GOALS=Goals/*.cpp
STRATS=Strategies/*.cpp
TACTICS=Tactics/*.cpp
CHAINS=Chains/*.cpp
UTIL=Util/*.cpp

EXECUTABLE=smashbot

all: util goals strats tactics chains main
	$(CC) $(LDFLAGS) *.o -o $(EXECUTABLE)

.PHONY: main
.PHONY: util
.PHONY: goals
.PHONY: strats
.PHONY: tactics
.PHONY: chains
.PHONY: clean

main:
	$(CC) $(CFLAGS) $(SOURCES)

util:
	./Util/constants.py
	$(CC) $(CFLAGS) $(UTIL)

goals:
	$(CC) $(CFLAGS) $(GOALS)

strats:
	$(CC) $(CFLAGS) $(STRATS)

tactics:
	$(CC) $(CFLAGS) $(TACTICS)

chains:
	$(CC) $(CFLAGS) $(CHAINS)

clean:
	rm -f *.o */*.o *.d */*.d smashbot
