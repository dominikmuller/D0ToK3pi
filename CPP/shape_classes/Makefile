###############################################################################
# Build shared library objects from ROOT classes.
###############################################################################

# Header file extension
H_EXT = h
# Implementation file extension
C_EXT = cxx

# Directory containing the header and implementation files
SRC = .

# Build a list of names of classes to created shared library objects for
SHAPES := $(shell ls $(SRC) | egrep "$(C_EXT)$$" | sed 's/\(.*\)\.$(C_EXT)/\1.so/' | egrep "Dict$$" --invert)

# Compilation flags
CXXFLAGS := -g -O -fPIC -Wall $(shell root-config --cflags)
# Linking flags
LDFLAGS := -O $(shell root-config --libs) -lRooFitCore -lRooFit

# Compiler
CC = g++
# Linker
LD = g++

# Build all shape objects when running bare `make`
all: $(SHAPES)

# Build dictionary files from headers
%_Dict.$(C_EXT): %.$(H_EXT)
	@echo rootcint $@
	@rootcint -f $@ -c -p $<

# Build objects from dictionaries
%.o: %_Dict.$(C_EXT)
	@echo CC $@
	@$(CC) -c -o $@ $(CXXFLAGS) $^

# Build shared libraries from objects and implementation files
%.so: %.o %.$(C_EXT)
	@echo LD $@
	@$(LD) -shared -o $@ $(LDFLAGS) $(CXXFLAGS) $^

# Clean up build files
clean:
	@rm -f Roo*_Dict.cxx
	@rm -f Roo*_rdict.pcm
	@rm -f Roo*.o
	@rm -f Roo*.so
	@rm -rf Roo*.dSYM
