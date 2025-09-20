CC=g++
DLIBS=-lbcm2835
epd:main.o epd0579RYS683.o imagedata.o epdif.o
	$(CC) -Wall -o epd main.o epd0579RYS683.o imagedata.o epdif.o $(DLIBS)
imagedata.o:imagedata.cpp imagedata.h 
	$(CC) -Wall -c imagedata.cpp $(DLIBS)
epd0579RYS683.o:epd0579RYS683.cpp epd0579RYS683.h
	$(CC) -Wall -c epd0579RYS683.cpp $(DLIBS)
epdif.o:epdif.cpp epdif.h
	$(CC) -Wall -c epdif.cpp $(DLIBS)
main.o:main.cpp epd0579RYS683.h imagedata.h
	$(CC) -Wall -c main.cpp $(DLIBS)
clean:
	rm imagedata.o main.o epd0579RYS683.o epdif.o epd

