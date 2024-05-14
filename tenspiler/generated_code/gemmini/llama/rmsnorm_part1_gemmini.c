
// include statements
#include "include/gemmini_params.h"
#include "include/gemmini.h"
//# define LEN 200, change as needed
//note elem_t is defined in gemmini_params.h and is defaulted to int8_t

void rmsnorm_part1_gemmini(elem_t input[LEN][LEN], elem_t weight[LEN][LEN], elem_t* out){
    static elem_t temp0[LEN][LEN]; 
    for (int i = 0; i < LEN; i++) { 
     	 temp0[i][0] = input[i][0] * input[i][0]; 
     } 
    tiled_global_average(temp0[0], (elem_t*) out, 1, 1, 1, 1); 
    *out = *out * LEN * LEN; 

}

float rmsnorm_part1_gemmini_glued (float input[LEN], float weight[LEN]){
    static elem_t glued_5[LEN][LEN];

    for (int i = 0; i < LEN; i++) {
        glued_5[i][0] = input[i];
    }

    static elem_t glued_6[LEN][LEN];

    for (int i = 0; i < LEN; i++) {
        glued_6[i][0] = weight[i];
    }

    elem_t out;
    rmsnorm_part1_gemmini(glued_5, glued_6, &out);

    return out;
}
