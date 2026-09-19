#include <stdio.h>
#include <stdlib.h>
#include <math.h>


struct vector
{
    float *components;
    int dimensions;
};


struct vector vector_from_array(float *arr, int dimensions){
    struct vector v;
    v.dimensions = dimensions;
    v.components = malloc(dimensions * sizeof(float));
    for (int i = 0; i < dimensions; i++){
        v.components[i] = arr[i];
    }
    return v;
}


void free_vector(struct vector *v){
    free(v->components);
    v->components = NULL;
    v->dimensions = 0;
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
    c.components = NULL;
    c.components = malloc(c.dimensions * sizeof(float));


    for (int i = 0; i < a.dimensions; i++){
        c.components[i] = a.components[i] + b.components[i];
    }

    return c;
}


struct vector vector_subtract(struct vector a, struct vector b){
    cmp_dim(a, b);
    struct vector c;

    c.dimensions = a.dimensions;
    c.components = NULL;
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


int vector_equality(struct vector a, struct vector b){
    if (a.dimensions != b.dimensions){
        return 0;
    }

    for (int i = 0; i < a.dimensions; i++){
        if (a.components[i] != b.components[i]){
            return 0;
        }
    }
    return 1;
}


struct vector vector_negate(struct vector a){
    struct vector c;

    c.dimensions = a.dimensions;
    c.components = NULL;
    c.components = malloc(c.dimensions * sizeof(float));

    for (int i = 0; i < a.dimensions; i++){
        c.components[i] = -1 * a.components[i];
    }
    return c;

}


struct vector vector_div(struct vector a, float b){
    struct vector c;

    c.dimensions = a.dimensions;
    c.components = NULL;

    if (b == 0 || a.dimensions == 0){
        return c; 
    }

    c.components = malloc(c.dimensions * sizeof(float));

    for (int i = 0; i < a.dimensions; i++){
        c.components[i] = a.components[i] / b;
    }

    return c;
}


float vector_magnitude(struct vector a){
    float result = 0.0f;

    for (int i = 0; i < a.dimensions; i++){
        result += a.components[i] * a.components[i];
    }
    return sqrt(result);
}


struct vector vector_normalized(struct vector a){
    return vector_div(a, vector_magnitude(a));
}


float vector_scalar_mul(struct vector a, struct vector b){
    float result;

    for (int i = 0; i < a.dimensions; i++){
        result += a.components[i] * b.components[i];
    }
    return result;
}


int main(){
    return 0;
}