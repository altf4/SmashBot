CC=g++
CFLAGS=-c -Wall -std=gnu++11
LDFLAGS=
SOURCES=cpu.cpp Controller.cpp Tactics/CloseDistance.cpp Strategies/Bait.cpp Goals/KillOpponent.cpp Chains/SHDL.cpp
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=cpu

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.cpp.o:
	$(CC) $(CFLAGS) $< -o $@
