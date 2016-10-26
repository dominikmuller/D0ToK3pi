ROOTLIBS=$(shell root-config --libs) -lMLP -lXMLIO -lTreePlayer
ROOTCFLAGS=$(shell root-config --cflags)

PYTHONLIBS=-L/afs/cern.ch/sw/lcg/releases/LCG_84/Python/2.7.10/x86_64-slc6-gcc49-opt/lib $(shell python-config --libs)
PYTHONCFLAGS=$(shell python-config --cflags)

LDFLAGS= -L./lib -lboost_program_options -fPIC #-lTools
CC=g++
ODIR=./obj
SRCDIR=./src


ifeq ($(CC), clang++)
	CFLAGS  = -g -O0 -I./include/ -Wall -std=c++11 -fPIC -stdlib=libc++
	LDFLAGS= -L./lib -lboost_program_options -fPIC -lm
else
	CFLAGS  = -g -O0 -I./include/ -Wall -std=c++11 -fPIC
	LDFLAGS= -L./lib -lboost_program_options -fPIC -lm -lstdc++ 
endif

RCXX= $(CFLAGS) $(ROOTCFLAGS)

_Objects_TreeSplitter=TreeSplitter.o AnyWriter.o DConfig.o MyUtils.o ROOTex.o
Objects_TreeSplitter=$(patsubst %,$(ODIR)/%,$(_Objects_TreeSplitter))


all: lib/treesplitter.so lib/libROOTex.so

lib/treesplitter.so: lib/libROOTex.so
	clang++ -O3 -shared -o $@ -fPIC -g -std=c++11 -I./include $(RCXX) $(PYTHONCFLAGS) src/TreeSplitter.cxx $(ROOTLIBS) $(PYTHONLIBS) -L./lib/ -lROOTex

dict/MyDict.cxx: include/ROOTex.h include/LinkDef.h
	rootcint -f $@ -c -p $^
	ln -s ../dict/MyDict_rdict.pcm lib
	ln -s ../dict/MyDict_rdict.pcm bin
 
lib/libROOTex.so: $(ODIR)/ROOTex.o
	g++ -shared -o $@ `root-config --ldflags` $(ROOTLIBS) -fPIC -I./dict/ -I./ $(RCXX) $^

$(ODIR)/ROOTex.o: dict/MyDict.cxx
	$(CC) -c -o $@ $< -I./ $(RCXX)

$(ODIR)/%.o: $(SRCDIR)/%.cxx
	$(CC) -c -o $@ $< $(RCXX)


clean:
		@rm -f *~
		@rm -f $(ODIR)/*.o 
		@rm -f lib/*.so 
		@rm -f ./bin/*.x
		@rm -f ./dict/*.cxx
		@rm -f ./*/*.pcm
