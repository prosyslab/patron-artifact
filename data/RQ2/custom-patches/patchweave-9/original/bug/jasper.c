
#include <stdint.h>
#include <stdio.h>
#define EOF (-1)


typedef uint_least32_t uint32_t;
typedef uint_least64_t uint64_t;


typedef struct jpc_siz {
  uint32_t width;
  uint32_t height;
  uint32_t tilewidth;
  uint32_t tileheight;
  uint32_t tilexoff;
  uint32_t tileyoff;
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

typedef struct jpc_dec {
  uint32_t xend;
  uint32_t yend;
  uint32_t tilewidth;
  uint32_t tileheight;
  uint32_t tilexoff;
  uint32_t tileyoff;
  uint32_t numhtiles;
  uint32_t numvtiles;
} jpc_dec_t;

typedef struct jas_stream {
  int *dummy;
} jas_stream_t;

void init_source(jpc_ms_t *ms, jas_stream_t *in) {
  FILE *fp = fopen("dummy.c", "rb");
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

  // if (siz->tilexoff >= siz->width) {
	// 	jas_eprintf("all tiles are outside the image area\n");
	// 	return -1;
	// }

  return 0;
}

int jpc_dec_process_siz(jpc_dec_t *dec, jpc_ms_t *ms) {

  jpc_siz_t *siz = &ms->parms.siz;
	dec->xend = siz->width;
	dec->yend = siz->height;
  dec->tilewidth = siz->tilewidth;
	dec->tileheight = siz->tileheight;
	dec->tilexoff = siz->tilexoff;
	dec->tileyoff = siz->tileyoff;

  dec->numhtiles = (((dec->xend - dec->tilexoff) + dec->tilewidth) - 1) / dec->tilewidth;
  dec->numvtiles = (((dec->yend - dec->tileyoff) + dec->tileheight) - 1) / dec->tileheight;

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