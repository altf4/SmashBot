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

all: goals strats tactics chains main util
	$(CC) $(LDFLAGS) *.o -o $(EXECUTABLE)

.PHONY: main
.PHONY: goals
.PHONY: strats
.PHONY: tactics
.PHONY: chains
.PHONY: util
.PHONY: clean

main:
	$(CC) $(CFLAGS) $(SOURCES)

goals:
	$(CC) $(CFLAGS) $(GOALS)

strats:
	$(CC) $(CFLAGS) $(STRATS)

tactics:
	$(CC) $(CFLAGS) $(TACTICS)

chains:
	$(CC) $(CFLAGS) $(CHAINS)

util:
	$(CC) $(CFLAGS) $(UTIL)

clean:
	rm -f *.o */*.o *.d */*.d smashbot
