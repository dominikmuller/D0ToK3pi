ROOTLIBS=$(shell root-config --libs) -lMLP -lXMLIO -lTreePlayer
ROOTCFLAGS=$(shell root-config --cflags)

PYTHONLIBS=$(shell python3.6-config --ldflags)
PYTHONCFLAGS=$(shell python3.6-config --cflags)

CC=g++
ODIR=./obj
SRCDIR=./src


ifeq ($(CC), clang++)
	CFLAGS  = -g -O0 -I./include/ -Wall -std=c++11 -fPIC -stdlib=libc++
	#LDFLAGS= -L./lib -lboost_program_options -fPIC -lm
else
	CFLAGS  = -g -O0 -I./include/ -Wall -std=c++11 -fPIC
	#LDFLAGS= -lstdc++ 
endif

RCXX= $(CFLAGS) $(ROOTCFLAGS)

_Objects_TreeSplitter=TreeSplitter.o AnyWriter.o DConfig.o MyUtils.o ROOTex.o
Objects_TreeSplitter=$(patsubst %,$(ODIR)/%,$(_Objects_TreeSplitter))


all: lib/k3pi_cpp.so lib/libROOTex.so

lib/k3pi_cpp.so: lib/libROOTex.so
	$(CC) -O3 -shared -o $@ -fPIC -g -std=c++11 -I./include $(RCXX) $(PYTHONCFLAGS) src/phsp_variables.cpp src/delta_m.cpp src/masses.cpp src/double_misid.cpp src/delta_angle.cpp src/bindings.cpp src/TreeSplitter.cpp $(LDFLAGS) $(ROOTLIBS) $(PYTHONLIBS)

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
