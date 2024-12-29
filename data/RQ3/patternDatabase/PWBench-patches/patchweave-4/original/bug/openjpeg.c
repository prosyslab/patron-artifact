#include <stdio.h>
#include <stdint.h>
#define EVT_ERROR 1

typedef struct opj_cio {
  unsigned char *bp;
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
} opj_j2k_t;

typedef struct opj_cp {
  int tw, th, tdx, tdy;
  opj_tcp_t *tcps;
} opj_cp_t;


void init_source(opj_j2k_t *j2k) {
  int *fp = fopen("dummy.c", "rb");
  j2k->cio = malloc(sizeof(opj_cio_t));
  j2k->image = malloc(sizeof(opj_image_t));
  j2k->cio->bp = malloc(1028);
  read(fp, j2k->cio->bp, 1028);
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

void j2k_read_siz(opj_j2k_t *j2k) {

  opj_cio_t *cio = j2k->cio;
	opj_image_t *image = j2k->image;
  opj_cp_t *cp = j2k->cp;

  image->x1 = cio_read(cio, 4);	/* Xsiz */
	image->y1 = cio_read(cio, 4);	/* Ysiz */
  
  cp->tdx = cio_read(cio, 4);		/* XTsiz */
	cp->tdy = cio_read(cio, 4);		/* YTsiz */
	cp->tx0 = cio_read(cio, 4);		/* XT0siz */
	cp->ty0 = cio_read(cio, 4);		/* YT0siz */
  
  cp->tw = (((image->x1 - image->tx0) + cp->tdx) - 1) / cp->tdx;
	cp->th = (((image->y1 - image->ty0) + cp->tdy) - 1) / cp->tdy;
  
  // if (cp->tw == 0 || cp->th == 0 || cp->tw > 65535 / cp->th) {
  //   opj_event_msg(j2k->cinfo, EVT_ERROR, 
  //                           "Invalid number of tiles : %u x %u (maximum fixed by jpeg2000 norm is 65535 tiles)\n",
  //                           cp->tw, cp->th);
  //   return;
  // }

  cp->tcps = (opj_tcp_t*) opj_calloc(cp->tw * cp->th, sizeof(opj_tcp_t));

}
int main(int argc, char **argv) {
  opj_j2k_t j2k;
  init_source(&j2k);
  j2k_read_siz(&j2k);
  return 0;
  
}