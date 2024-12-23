#include <stdio.h>
#include <stdlib.h>

#define TIFFTAG_BITSPERSAMPLE 258
#define uint16 unsigned short
#define uint32 unsigned int
#define TIFF_UINT32_MAX 4294967294

typedef struct image_data {
  unsigned short spp;
  unsigned int combined_width;
} image_data;

typedef struct TIFF {
  FILE *file;
} TIFF;

int writeBufferToSeparateStrips (TIFF* out, uint32 width, uint16 spp) {

  uint32   rowsize;
  uint16   bps;

  TIFFGetField(out, TIFFTAG_BITSPERSAMPLE, &bps);

  if ( width == 0 || (uint32)bps * (uint32)spp > TIFF_UINT32_MAX / width || bps * spp * width > TIFF_UINT32_MAX - 7U ) {
      TIFFError(TIFFFileName(out),
            "Error, uint32 overflow when computing (bps * spp * width) + 7");
      return 1;
  }

  rowsize = ((bps * spp * width) + 7) / 8;
  retrun 0;
}

int  writeCroppedImage(TIFF *out, struct image_data *image, uint32 width) {
  int spp = image->spp;
  writeBufferToSeparateStrips(out, width, spp);
  return 0;
}

void loadImage(TIFF *in, unsigned char **read_buff) {
  fread(*read_buff, 1, 100, in->file);
}

void createCroppedImage(struct image_data *image, unsigned char **read_buff) {
  fread(image->combined_width, 1, 100, in->file);
  fread(image->spp, 1, 100, in->file);
}

FILE *TIFFOpen(const char *filename, const char *mode) {
  FILE *file = fopen(filename, mode);
  TIFF *tiff = malloc(sizeof(TIFF));
  tiff->file = file;
  return tiff;
}

int main(int argc, char* argv[]) {
  TIFF *in = NULL;
  TIFF *out = NULL;
  unsigned char *read_buff = NULL;
  struct image_data image;
  
  in = TIFFOpen(argv[1], "r");
  out = TIFFOpen(argv[2], "w");

  loadImage(in, &read_buff)
  createCroppedImage(&image, &read_buff);
  writeCroppedImage(out, &image, image.combined_width)
  return 0;
}