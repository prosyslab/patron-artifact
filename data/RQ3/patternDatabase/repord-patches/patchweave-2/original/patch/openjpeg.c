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
extern int opj_event_msg(int, const char *, ...);

void init_source(opj_j2k_t *j2k) {
  int *fp = fopen("dummy.c", "rb");
  j2k->cio = malloc(sizeof(opj_cio_t));
  j2k->image = malloc(sizeof(opj_image_t));
  j2k->cio->bp = malloc(1028);
  read(fp, j2k->cio->bp, 1028);
  fclose(fp);
  
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

  image->x1 = cio_read(cio, 4);	/* Xsiz */
	image->y1 = cio_read(cio, 4);	/* Ysiz */
	image->x0 = cio_read(cio, 4);	/* X0siz */
	image->y0 = cio_read(cio, 4);	/* Y0siz */

  image->comps.dx = cio_read(cio, 1);	/* XRsiz_i */
	image->comps.dy = cio_read(cio, 1);	/* YRsiz_i */

  if (!(image->comps.dx * image->comps.dy)) {
    opj_event_msg(EVT_ERROR,  "JPWL: invalid component size (dx: %d, dy: %d)\n", image->comps.dx, image->comps.dy);
    return;
  }

  int w = (((image->x1 - image->x0) + image->comps.dx) - 1) / image->comps.dx;
	int h = (((image->y1 - image->y0) + image->comps.dy) - 1) / image->comps.dy;
  
}
int main(int argc, char **argv) {
  opj_j2k_t j2k;
  init_source(&j2k);
  j2k_read_siz(&j2k);
  return 0;
  
}