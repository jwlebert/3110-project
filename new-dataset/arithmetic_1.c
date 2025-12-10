#include <math.h>
#include <stdio.h>

#define MAX 8 
#define MAXBIN 127

int magnitude(int x[]) {
    int value = 0;
    int exponent = 0;

    for (int i = MAX - 1; i > 0; i--) {
        value += x[i] * pow(2, exponent);
        exponent++;
    }
    return value;
}

char max(int a[], int b[]) {
    return (magnitude(a) > magnitude(b)) ? 'a' : 'b';
}

void operate(int operation, int a[], int b[], int result[]) { // 0 for subtract, 1 for add
    for (int i = MAX - 1; i > -1; i--) {
        if (operation) {
            result[i] = a[i] + b[i]; // Adding

            if (result[i] > 1) { // Carry component
                result[i] %= 2;
                a[i-1] += 1;
            }
        } else {
            result[i] = a[i] - b[i];
        }
    }

}

void func_signed_mag_addition(int a[], int b[], int result[]) {
    if (a[0] == b[0]) { // Both positive
        operate(1, a, b, result);
        if (a[0] == 1) { // If a (and b, by extension) are negative
            result[0] = 1;
        }
    } else if (max(a, b) == 'a') {
        operate(0, a, b, result);
        if (a[0] == 0) {
            result[0] = 0;
        }
    } else if (max(a, b) == 'b') {
        operate(0, b, a, result);
        if (b[0] == 0) {
            result[0] = 0;
        }
    }

    if (magnitude(a) + magnitude(b) > MAXBIN) {
        puts("Overflow!");
    }
}

void func_signed_mag_subtraction(int a[], int b[], int result[]) {
    if (a[0] == 0 && b[0] == 1) { //
        operate(1, a, b, result);
    } else if (a[0] == 1 && b[0] == 0) {
        operate(1, a, b, result);
        result[0] = 1;
    } else if (a[0] == 0 && b[0] == 0) {
        if (max(a, b) == 'a') {
            operate(0, a, b, result);
        } else {
            operate(0, b, a, result);
            result[0] = 1;
        }
    } else if (a[0] == 1 && b[0] == 1) {
        if (max(a, b) == 'b') {
            operate(0, b, a, result);
            result[0] = 0;
        } else {
            operate(0, a, b, result);
            result[0] = 1;
        }
    }
    
    if (magnitude(a) + magnitude(b) > MAXBIN) {
        puts("Overflow!");
    }
}