
#include <stdint.h>
#include <stdio.h>
#define EOF (-1)


// typedef uint_least32_t unsigned int;
// typedef uint_least64_t uint64_t;


typedef struct jpc_siz {
  unsigned int width;
  unsigned int height;
  unsigned int tilewidth;
  unsigned int tileheight;
  unsigned int tilexoff;
  unsigned int tileyoff;
  unsigned int xoff;
} jpc_siz_t;

typedef struct jpc_params {
  jpc_siz_t siz;
} jpc_params_t;

typedef struct jpc_ms {
  jpc_params_t parms;
} jpc_ms_t;

typedef struct jpc_cstate {
  int dummy;
} jpc_cstate_t;

typedef struct jpc_dec_tile {
  unsigned int xstart;
} jpc_dec_tile_t;

typedef struct jpc_dec {
  unsigned int xend;
  unsigned int yend;
  unsigned int tilewidth;
  unsigned int tileheight;
  unsigned int tilexoff;
  unsigned int tileyoff;
  unsigned int numhtiles;
  unsigned int numvtiles;
  unsigned int numtiles;
  unsigned int xstart;
  jpc_dec_tile_t *tiles;
} jpc_dec_t;

typedef struct jas_stream {
  int *dummy;
} jas_stream_t;



void init_source(jpc_ms_t *ms, jas_stream_t *in) {
  int *fp = fopen("dummy.c", "rb");
  ms->parms.siz.width = 0;
  ms->parms.siz.height = 0;
  ms->parms.siz.tilewidth = 0;
  ms->parms.siz.tileheight = 0;
  ms->parms.siz.tilexoff = 0;
  ms->parms.siz.tileyoff = 0;
  in->dummy = malloc(1028);
  fread(in->dummy, 1028, 1, fp);
  fclose(fp);
}

int jas_stream_getc(jas_stream_t *in) {
  return *in->dummy++;
}

int jpc_getuint32(jas_stream_t *in, unsigned int *val)
{
	unsigned int v;
	int c;
	if ((c = jas_stream_getc(in)) == EOF) {
		return -1;
	}
	v = c;
	if ((c = jas_stream_getc(in)) == EOF) {
		return -1;
	}
	v = (v << 8) | c;
	if ((c = jas_stream_getc(in)) == EOF) {
		return -1;
	}
	v = (v << 8) | c;
	if ((c = jas_stream_getc(in)) == EOF) {
		return -1;
	}
	v = (v << 8) | c;
	if (val) {
		*val = v;
	}
	return 0;
}

int jpc_siz_getparms(jpc_ms_t *ms, jpc_cstate_t *cstate, jas_stream_t *in) {

  jpc_siz_t *siz = &ms->parms.siz;
  
  jpc_getuint32(in, &siz->width);
	jpc_getuint32(in, &siz->height);
  jpc_getuint32(in, &siz->tilewidth);
  jpc_getuint32(in, &siz->tileheight);
  jpc_getuint32(in, &siz->tilexoff); 
	jpc_getuint32(in, &siz->tileyoff);
  jpc_getuint32(in, &siz->xoff);

  if (siz->tilexoff > siz->xoff || siz->tilexoff + siz->tilewidth <= siz->xoff) {
		jas_eprintf("XTOsiz not in permissible range\n");
		return -1;
	}

  return 0;
}

int jpc_dec_process_siz(jpc_dec_t *dec, jpc_ms_t *ms) {

  jpc_siz_t *siz = &ms->parms.siz;
  jpc_dec_tile_t *tile;

  dec->xstart = siz->xoff;
	dec->xend = siz->width;
	dec->yend = siz->height;
  dec->tilewidth = siz->tilewidth;
	dec->tileheight = siz->tileheight;
	dec->tilexoff = siz->tilexoff;
	dec->tileyoff = siz->tileyoff;


  dec->numhtiles = (((dec->xend - dec->tilexoff) + dec->tilewidth) - 1) / dec->tilewidth;
  dec->numvtiles = (((dec->yend - dec->tileyoff) + dec->tileheight) - 1) / dec->tileheight;
  dec->numtiles = dec->numhtiles * dec->numvtiles;
  dec->tiles = calloc(dec->numtiles, sizeof(jpc_dec_tile_t));

  for (int tileno = 0; tileno < dec->numtiles; ++tileno) {

    int htileno = tileno % dec->numhtiles;
    unsigned int start = (dec->tilexoff + htileno * dec->tilewidth) > dec->xstart ? (dec->tilexoff + htileno * dec->tilewidth) : dec->xstart;
  }


  return 0;
}

int main(int argc, char **argv) {
  jpc_ms_t ms;
  jpc_cstate_t cstate;
  jas_stream_t in;
  jpc_dec_t dec;
  init_source(&ms, &in);
  jpc_siz_getparms(&ms, &cstate, &in);
  jpc_dec_process_siz(&dec, &ms);
  return 0;
}