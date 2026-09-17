#include <stdio.h>
#include <stdlib.h>

struct vector
{
    float *components;
    int dimensions;
};


void free_vector(struct vector v){
    free(v.components);
}

void cmp_dim(struct vector a, struct vector b){
    if (a.dimensions != b.dimensions){
        exit(1);
    }
}


struct vector vector_add(struct vector a, struct vector b){
    cmp_dim(a, b);
    struct vector c;

    c.dimensions = a.dimensions;
    c.components = malloc(c.dimensions * sizeof(float));


    for (int i = 0; i < a.dimensions; i++){
        c.components[i] = a.components[i] + b.components[i];
    }

    return c;
}


struct vector vector_substract(struct vector a, struct vector b){
    cmp_dim(a, b);
    struct vector c;

    c.dimensions = a.dimensions;
    c.components = malloc(c.dimensions * sizeof(float));


    for (int i = 0; i < a.dimensions; i++){
        c.components[i] = a.components[i] - b.components[i];
    }

    return c;
}


struct vector vector_multiplication(struct vector a, struct vector b){
    cmp_dim(a, b);
    struct vector result;
    result.dimensions = 0;
    result.components = NULL;  

    if (a.dimensions == 2){
        result.dimensions = 1;
        result.components = malloc(result.dimensions * sizeof(float));
        result.components[0] = a.components[0] * b.components[1] - a.components[1] * b.components[0];
        return result;
    }


    if (a.dimensions == 3){
        result.dimensions = 3;
        result.components = malloc(result.dimensions * sizeof(float));
        result.components[0] = a.components[1] * b.components[2] - a.components[2] * b.components[1];
        result.components[1] = a.components[2] * b.components[0] - a.components[0] * b.components[2];
        result.components[2] = a.components[0] * b.components[1] - a.components[1] * b.components[0];
        return result;
    }

    return result;
}




int main(){
    return 0;
}