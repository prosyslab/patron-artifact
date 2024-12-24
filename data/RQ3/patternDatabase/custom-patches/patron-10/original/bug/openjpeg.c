#include <stdio.h>
#include <stdlib.h>

#define OPJ_BYTE unsigned char
#define OPJ_UINT32 unsigned int

typedef struct opj_cp_t {
  OPJ_UINT32 ppm_len;
  OPJ_BYTE *ppm_data;
} opj_cp_t;

typedef struct opj_j2k_t {
  struct opj_cp_t m_cp;
} opj_j2k_t;

void init_source(OPJ_BYTE *header_data) {
  FILE *file = fopen("test.txt", "r");
  fread(header_data, 1, 100, file);
  fclose(file);
}

void opj_read_bytes(OPJ_BYTE *p_header_data, OPJ_UINT32 *p_value, OPJ_UINT32 p_size) {
  *p_value = 0;
  for (OPJ_UINT32 i = 0; i < p_size; i++) {
    *p_value = (*p_value << 8) + p_header_data[i];
  }
}

int j2k_read_ppm_v3 (opj_j2k_t *p_j2k, OPJ_BYTE * p_header_data) {

  OPJ_BYTE *new_ppm_data;
  opj_cp_t *l_cp = &(p_j2k->m_cp);
  OPJ_UINT32 l_N_ppm = 0;
  
  opj_read_bytes(p_header_data, &l_N_ppm, 4);
  l_cp->ppm_len = l_N_ppm;
  l_cp->ppm_data = calloc(1, l_cp->ppm_len);
  
  opj_read_bytes(p_header_data, &l_N_ppm, 4);

  // if ((l_cp->ppm_len + l_N_ppm) < l_N_ppm) {
  //   opj_free(l_cp->ppm_data);
  //   opj_event_msg("Not enough memory to increase the size of ppm_data to add the new (complete) Ippm series\n");
  //   return OPJ_FALSE;
  // }
  new_ppm_data = (OPJ_BYTE *) realloc(l_cp->ppm_data, l_cp->ppm_len + l_N_ppm);

}

int main(int argc, char* argv[]) {
  opj_j2k_t j2k;
  OPJ_BYTE *header_data = malloc(100 * sizeof(OPJ_BYTE));
  init_source(header_data);
  j2k_read_ppm_v3(&j2k, header_data);
  return 0;
}