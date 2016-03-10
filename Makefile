CC=g++
CFLAGS=-g -c -Wall -std=gnu++11
LDFLAGS=-g -Wall -std=gnu++11

SOURCES=cpu.cpp
GOALS=Goals/*.cpp
STRATS=Strategies/*.cpp
TACTICS=Tactics/*.cpp
CHAINS=Chains/*.cpp
UTIL=Util/*.cpp

EXECUTABLE=cpu

all: goals strats tactics chains main util
	$(CC) $(LDFLAGS) *.o -o $(EXECUTABLE)

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
	rm -f *.o */*.o *.d */*.d cpu
