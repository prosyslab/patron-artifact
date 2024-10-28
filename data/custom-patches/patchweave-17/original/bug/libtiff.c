#include <stdio.h>

typedef struct BMPInfoHeader {
  unsigned int iWidth;
  unsigned int iHeight;
  unsigned int iBitCount;
} BMPInfoHeader;


int main(int argc, char **argv) {
  unsigned int size, width;
  char *scanbuf;
  int iShort;
  BMPInfoHeader info_hdr;
  char *infilename = argv[1];
  int *fd = open(infilename, "r");
  read(fd, &info_hdr.iWidth, 4);
  read(fd, &info_hdr.iBitCount, 2);
  read(fd, &iShort, 2);
  info_hdr.iWidth = iShort;
  width = info_hdr.iWidth;

  size = ((width * info_hdr.iBitCount + 31) & ~31) / 8;
  // size = width * info_hdr.iBitCount + 31;
	// 	if (!width || !info_hdr.iBitCount
	// 	    || (size - 31) / info_hdr.iBitCount != width )
	// 	{
	// 		TIFFError(infilename,
	// 			  "Wrong image parameters; "
	// 			  "can't allocate space for scanline buffer");
	// 		goto bad3;
	// 	}
  // size = (size & ~31) / 8;
  scanbuf = (char *) malloc(size);
}