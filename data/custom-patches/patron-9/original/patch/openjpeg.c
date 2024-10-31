#include <stdio.h>
#include <stdlib.h>

typedef struct opj_pi_comp_t {
  unsigned int dx;
  unsigned int dy;
  unsigned int numresolutions;
} opj_pi_comp_t;

typedef struct opj_pi_iterator_t {
  opj_pi_comp_t *comps;
  unsigned int tx0;
  unsigned int resno;
} opj_pi_iterator_t;

void init_source(opj_pi_iterator_t * pi) {
  opj_pi_comp_t comp;
  FILE *file = fopen("test.txt", "r");
  fread(&comp.dx, 1, 100, file);
  fread(&comp.dy, 1, 100, file);
  fread(&comp.numresolutions, 1, 100, file);
  pi->comps = &comp;
  fread(&pi->tx0, 1, 100, file);
  fread(&pi->resno, 1, 100, file);
  fclose(file);

}

int opj_pi_next_rpcl(opj_pi_iterator_t * pi) {
  
  opj_pi_comp_t comp = *(pi->comps);  
  unsigned int levelno = comp->numresolutions - 1 - pi->resno;

  if (((comp->dx << levelno) >> levelno) != comp->dx) {
    return -1;
  }
  
  int trx0 = (pi->tx0 + (comp->dx << levelno) - 1) / (comp->dx << levelno);
  return trx0;
}

int main(int argc, char* argv[]) {
  opj_pi_iterator_t pi;
  init_source(&pi);
  opj_pi_next_rpcl(&pi);
  return 0;
}