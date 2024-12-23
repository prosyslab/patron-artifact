#include <stdio.h>
#include <stdint.h>
#define EVT_ERROR 1

typedef struct opj_tcp {
  int tw, th, tdx, tdy;
} opj_tcp_t;

typedef struct opj_cp {
  int tx0, ty0, tdx, tdy;
  int tw, th;
  opj_tcp_t *tcps;
} opj_cp_t;

typedef struct opj_cio {
  unsigned char *bp;
  unsigned char *end;
} opj_cio_t;

typedef struct opj_image {
  int x0, y0, x1, y1;
  struct {
    int dx, dy;
  } comps;
} opj_image_t;

typedef struct opj_j2k {
  struct opj_cio *cio;
  struct opj_image *image;
  struct opj_cp *cp;
  void *cinfo;
} opj_j2k_t;

typedef struct opj_jp2_box {
  unsigned int length;
  unsigned int type;
} opj_jp2_box_t;

typedef struct opj_jp2 {
  struct opj_cio *cio;
  void *cinfo;
} opj_jp2_t;

void init_source(opj_jp2_t *jp2) {
  int *fp = fopen("dummy.c", "rb");
  int offset = 0;
  read(fp, &offset, 4);
  jp2->cio = malloc(sizeof(opj_cio_t));
  jp2->cio->bp = malloc(offset);
  jp2->cio->end = jp2->cio->bp + offset;
  read(fp, jp2->cio->bp, offset);

  fclose(fp);
  
}

int opj_event_msg(void *cinfo, int event, const char *fmt, ...) {
  return 0;
}

unsigned int cio_read(opj_cio_t *cio, int n) {
	int i;
	unsigned int v;
	v = 0;

	for (i = n - 1; i >= 0; i--) {
		v += (unsigned int)*cio->bp++ << (i << 3);
	}
	return v;
}

int jp2_read_boxhdr(void* cinfo, opj_cio_t *cio, opj_jp2_box_t *box) {
  box->length = cio_read(cio, 4);
  if (box->length == 0) {
    // if (cio->end - cio->bp < 8) {
		//   opj_event_msg(cinfo, EVT_ERROR, "Integer overflow in box->length\n");
		//   return -1; // TODO: actually check jp2_read_boxhdr's return value
	  // }
    box->length = cio->end - cio->bp + 8;
  }
  return 0;
}

int jp2_read_ihdr(opj_jp2_t *jp2, opj_cio_t *cio) {
	opj_jp2_box_t box;

	void* cinfo = jp2->cinfo;

  jp2_read_boxhdr(cinfo, cio, &box);

  return 0;
}

int main(int argc, char **argv) {
  opj_jp2_t jp2;
  init_source(&jp2);
  jp2_read_ihdr(&jp2, jp2.cio);
  return 0;
  
}