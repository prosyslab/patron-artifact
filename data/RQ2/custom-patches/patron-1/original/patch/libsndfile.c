#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef int FILE;

typedef struct SF_PRIVATE {
  FILE *file;
  int dataoffset;
  int dataend;
  int filelength;
  int bytewidth;
  int blockwidth;
  int datalength;
  int channels;
  int samplerate;
  int format;
  int frames;
} SF_PRIVATE;

int alaw_init (SF_PRIVATE *psf) {
	psf->bytewidth = 1 ;
	psf->blockwidth = psf->channels ;

  psf->datalength = (psf->dataend) ? psf->dataend - psf->dataoffset : psf->filelength - psf->dataoffset ;

	// psf->frames = psf->datalength / psf->blockwidth ;
	psf->frames = psf->blockwidth > 0 ? psf->datalength / psf->blockwidth : 1 ;

	return 0 ;
}

static int w64_read_header(SF_PRIVATE *psf) { 
  fread(&psf->channels, 1, 1, psf->file);
  fread(&psf->samplerate, 1, 1, psf->file);
  fread(&psf->format, 1, 1, psf->file);
  fread(&psf->frames, 1, 1, psf->file);
  fread(&psf->filelength, 1, 1, psf->file);
  fread(&psf->dataoffset, 1, 1, psf->file);
  fread(&psf->dataend, 1, 1, psf->file);
  fread(&psf->bytewidth, 1, 1, psf->file);
  return 0;

}

FILE *w64_open(SF_PRIVATE *psf) {
  w64_read_header(psf);
  alaw_init(psf);
  return psf->file;
}

FILE *psf_open_file(SF_PRIVATE *psf , int mode) {
  return w64_open(psf);
}

void psf_init_files(SF_PRIVATE *psf, char *path) {
  psf->channels = 1;
  psf->samplerate = 1;
  psf->format = 1;
  psf->frames = 1;
  psf->file = fopen(path, "rb");
  psf->dataoffset = 0;
  psf->dataend = 0;
  psf->filelength = 0;
  psf->bytewidth = 0;
  psf->blockwidth = 0;
  psf->datalength = 0;
  return;
}

FILE *sf_open(char const   *path , int mode) {
  SF_PRIVATE *psf ;
  psf = (SF_PRIVATE *) malloc(sizeof(SF_PRIVATE));
  psf_init_files(psf, path);
  return psf_open_file(psf, mode);
} 

static void info_dump(char const   *filename ) { 
  FILE *file;
  file = sf_open(filename, 16);
  if (file == NULL) {
    printf("Error");
    return;
  }
  return;
}

int main(int argc , char *argv[] ) {
  info_dump(argv[1]);
  return 0;
}