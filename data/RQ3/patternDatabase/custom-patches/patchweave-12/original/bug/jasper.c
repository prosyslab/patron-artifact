#define MIF_MAGICLEN 4

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define EOF (-1)

typedef struct jas_stream {
  int *fp;
  int *dummy;
} jas_stream_t;

void init_source(jas_stream_t *in) {
  in->fp = fopen("dummy.c", "rb");
  in->dummy = malloc(1028);
  fread(in->dummy, 1028, 1, in->fp);
  fclose(in->fp);
}

int jas_stream_getc(jas_stream_t *in) {
  return *in->dummy++;
}


int mif_validate(jas_stream_t *in)
{
        unsigned char buf[MIF_MAGICLEN];
        unsigned int magic;
        for (int i = 0; i < MIF_MAGICLEN; i++) {
                buf[i] = jas_stream_getc(in);
        }

        magic = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3];
        // magic = ((uint_fast32_t) buf[0] << 24) |
	//   ((uint_fast32_t) buf[1] << 16) |
	//   ((uint_fast32_t) buf[2] << 8) |
	//   buf[3];

        return 0;
}

int main(int argc, char **argv)
{
        jas_stream_t in;
        init_source(&in);
        mif_validate(&in);
        return ret;
}