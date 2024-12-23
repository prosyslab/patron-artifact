mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/uclouvain/openjpeg/ tmp
cd tmp;
git checkout 003759a4829f3f1baa5a2292956618fecf314818;
sed -i '1903i\static opj_sparse_array_int32_t* opj_dwt_init_sparse_array1(\
    opj_tcd_tilecomp_t* tilec,\
    OPJ_UINT32 numres)\
{\
    opj_tcd_resolution_t* tr_max = &(tilec->resolutions[numres - 1]);\
    OPJ_UINT32 w = (OPJ_UINT32)(tr_max->x1 - tr_max->x0);\
    OPJ_UINT32 h = (OPJ_UINT32)(tr_max->y1 - tr_max->y0);\
    OPJ_UINT32 resno, bandno, precno, cblkno;\
    opj_sparse_array_int32_t* sa = opj_sparse_array_int32_create(\
                                       w, h, opj_uint_min(w, 64), opj_uint_min(h, 64));\
    if (sa == NULL) {\
        return NULL;\
    }\
\
    for (resno = 0; resno < numres; ++resno) {\
        opj_tcd_resolution_t* res = &tilec->resolutions[resno];\
\
        for (bandno = 0; bandno < res->numbands; ++bandno) {\
            opj_tcd_band_t* band = &res->bands[bandno];\
\
            for (precno = 0; precno < res->pw * res->ph; ++precno) {\
                opj_tcd_precinct_t* precinct = &band->precincts[precno];\
                for (cblkno = 0; cblkno < precinct->cw * precinct->ch; ++cblkno) {\
                    opj_tcd_cblk_dec_t* cblk = &precinct->cblks.dec[cblkno];\
                    if (cblk->decoded_data != NULL) {\
                        OPJ_UINT32 x = (OPJ_UINT32)(cblk->x0 - band->x0);\
                        OPJ_UINT32 y = (OPJ_UINT32)(cblk->y0 - band->y0);\
                        OPJ_UINT32 cblk_w = (OPJ_UINT32)(cblk->x1 - cblk->x0);\
                        OPJ_UINT32 cblk_h = (OPJ_UINT32)(cblk->y1 - cblk->y0);\
\
                        if (band->bandno & 1) {\
                            opj_tcd_resolution_t* pres = &tilec->resolutions[resno - 1];\
                            x += (OPJ_UINT32)(pres->x1 - pres->x0);\
                        }\
                        if (band->bandno & 2) {\
                            opj_tcd_resolution_t* pres = &tilec->resolutions[resno - 1];\
                            y += (OPJ_UINT32)(pres->y1 - pres->y0);\
                        }\
\
                        if (!opj_sparse_array_int32_write(sa, x, y,\
                                                          x + cblk_w, y + cblk_h,\
                                                          cblk->decoded_data,\
                                                          1, cblk_w, OPJ_TRUE)) {\
                            opj_sparse_array_int32_free(sa);\
                            return NULL;\
                        }\
                    }\
                }\
            }\
        }\
    }\
\
    return sa;\
}' src/lib/openjp2/dwt.c
sed -i '2709s/sa = opj_dwt_init_sparse_array(tilec, numres);/sa = opj_dwt_init_sparse_array1(tilec, numres);/' src/lib/openjp2/dwt.c
$SCMAKE_BIN
sparrow -il -frontend claml sparrow/src/bin/jp2/opj_decompress.i sparrow/src/bin/jp2/convert* sparrow/src/bin/jp2/index.i sparrow/src/lib/openjp2/*.i > openjpeg.c;
cd ..;
mv tmp/openjpeg.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' full_patch/openjpeg.c
cp full_patch/openjpeg.c patch
sed -i '94531,94540d' patch/openjpeg.c
sed -i '94535,94539d' patch/openjpeg.c
cp patch/openjpeg.c bug
sed -i '93184,93193d' bug/openjpeg.c
sed -i '93198,93202d' bug/openjpeg.c